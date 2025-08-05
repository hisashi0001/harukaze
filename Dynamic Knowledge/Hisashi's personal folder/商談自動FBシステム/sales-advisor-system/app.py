#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional
from collections import deque
import threading
import queue

# FastAPI and WebSocket
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Google Cloud APIs
from google.cloud import speech
from google.oauth2 import service_account
import google.generativeai as genai

# Audio processing
import pyaudio
import wave
import io

# Set up Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service-account-key.json"
credentials = service_account.Credentials.from_service_account_file(
    "service-account-key.json"
)

# Initialize FastAPI app
app = FastAPI()

# Global variables
conversation_history = deque(maxlen=50)  # Store last 50 conversation turns
customer_profile = {}
current_phase = "diagnosis"
audio_queue = queue.Queue()
advice_queue = queue.Queue()
prior_information = ""  # 事前情報を格納

# Load knowledge base
with open("knowledge.json", "r", encoding="utf-8") as f:
    knowledge = json.load(f)

# Initialize Google Cloud clients
speech_client = speech.SpeechClient(credentials=credentials)

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyBb9u3cuNbzhjyNq8HQNUjSVl5nGOo9WCM"
genai.configure(api_key=GEMINI_API_KEY)

class AudioProcessor:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_recording = False
        
    def start_recording(self):
        """Start recording audio from microphone"""
        self.is_recording = True
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024,
            stream_callback=self.audio_callback
        )
        self.stream.start_stream()
        
    def audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio stream"""
        if self.is_recording:
            audio_queue.put(in_data)
        return (in_data, pyaudio.paContinue)
        
    def stop_recording(self):
        """Stop recording audio"""
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

class SpeechToTextProcessor:
    def __init__(self):
        self.config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="ja-JP",
            enable_automatic_punctuation=True,
            model="latest_long",  # Use the long audio model for better accuracy
            use_enhanced=True,  # Use enhanced model if available
            enable_word_confidence=True,  # Get confidence scores
            enable_speaker_diarization=True,  # Enable speaker separation
            diarization_speaker_count=2,  # Expect 2 speakers (salesperson and customer)
            speech_contexts=[speech.SpeechContext(
                phrases=["デザインスクール", "ポートフォリオ", "デザイナー", "UI", "UX", "Figma", "Photoshop"],
                boost=20.0  # Boost recognition of these terms
            )]
        )
        self.accumulated_audio = b""
        self.last_process_time = time.time()
        
    async def process_audio(self, audio_data):
        """Convert audio to text using Google Cloud Speech-to-Text"""
        try:
            audio = speech.RecognitionAudio(content=audio_data)
            response = speech_client.recognize(config=self.config, audio=audio)
            
            transcript = ""
            for result in response.results:
                # Get the most likely transcript
                if result.alternatives:
                    transcript += result.alternatives[0].transcript + " "
            
            return transcript.strip()
        except Exception as e:
            print(f"Speech recognition error: {e}")
            return ""

class AIAdvisor:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        print("Using Gemini 2.5 Flash model")
        
    async def generate_advice(self, transcript: str, context: Dict) -> Dict:
        """Generate sales advice based on conversation"""
        # Build prompt with knowledge base
        prompt = self._build_prompt(transcript, context)
        
        # Generate response
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=2048,
                    top_p=0.95,
                    top_k=64
                )
            )
        except Exception as e:
            print(f"Gemini API error: {e}")
            raise e  # Re-raise the error to handle it at a higher level
        
        # Parse response into structured advice
        advice = self._parse_response(response.text)
        return advice
        
    def _build_prompt(self, transcript: str, context: Dict) -> str:
        """Build prompt with sales knowledge"""
        # For continuous mode, don't label speakers
        if context.get("continuous"):
            recent_history = "\n".join([turn['text'] for turn in list(conversation_history)[-10:]])
        else:
            recent_history = "\n".join([f"{turn['speaker']}: {turn['text']}" for turn in list(conversation_history)[-15:]])
        
        # 連続会話モードの説明
        if context.get("continuous"):
            task_instruction = """
これは営業担当者と顧客の連続的な会話です。両者の声が混在している可能性があります。
文脈から誰が話しているかを判断し、会話の流れを理解してください。
「ですね」「そうですね」などの相槌ちは営業担当者、質問や懸念は顧客の可能性が高いです。
現在進行中の商談に対して、実践的なアドバイスを提供してください。
"""
        elif len(conversation_history) < 3:
            task_instruction = """
商談が始まったばかりです。まずは顧客との関係構築と情報収集に集中してください。
顧客の発言をしっかりと受け止め、共感を示しながら深掘りしていくことが重要です。
営業担当者は現在商談中であり、リアルタイムでのサポートが必要です。
"""
        else:
            task_instruction = """
商談の流れを分析し、現在のフェーズに応じた適切なアドバイスを提供してください。
これまでの会話の文脈を考慮し、顧客の本質的なニーズを見極めることが重要です。
営業担当者は現在商談中であり、即座に使える実践的なアドバイスが必要です。
"""
        
        prompt = f"""
あなたは優秀な営業コンサルタントです。営業担当者の成功をサポートするため、実践的で前向きなアドバイスを提供してください。

【営業の心構え（重要）】
1. 営業マンではなく「医者」であれ：課題の診断を完璧に行う
2. 商品を売るな、「未来」を売れ：顧客の望む理想の未来を描く
3. 問題を解決するな、「問題を再定義」せよ：より本質的な課題を発見する
4. 論破するな、「最強の味方」になれ：反論は救難信号として受け止める
5. ロジックで説得するな、「愛」で背中を押せ：最後は信念と熱量で動かす

【現在の商談フェーズと推奨アクション】
- 診断フェーズ：徹底的な傾聴（8割は聞く）、5W深掘り、小さな努力を承認
- 再定義フェーズ：業界の常識の嘘を指摘、例え話で本質を直感させる
- 未来提示フェーズ：ロードマップで道筋を示す、本音の欲求に刺さる未来を語る
- 決断促進フェーズ：反論を共感で受け止める、特別な期待を伝える

【事前情報】
{prior_information if prior_information else "なし"}

【最新の会話内容】
"{transcript}"

【これまでの会話の流れ】
{recent_history if recent_history else "（会話開始）"}

【顧客情報】
{json.dumps(customer_profile, ensure_ascii=False) if customer_profile else "まだ収集されていません"}

【現在のフェーズ】
{current_phase}

【重要な指示】
{task_instruction}

【タスク】
1. 会話全体から得られる情報を抽出（名前、会社、課題、予算、期限など）
2. 現在の商談フェーズを判定（診断/再定義/未来提示/決断促進）
3. 営業担当者が次に取るべき具体的なアクションを提案（営業の心構えに基づいて）
4. 優先度を設定（🔴緊急：重要なシグナル、🟡重要：フォローすべき点、🟢通常：順調な進行）

【注意事項】
- 連続的な会話から文脈を読み取る
- 誰が話しているかは内容から判断する
- アドバイスは具体的で実践的なものにする
- 批判的ではなく建設的なトーンで
- 営業マニュアルの原則に基づいた提案を心がける
- 必ずJSON形式のみで回答すること（説明文は不要）

以下のJSON形式で回答してください。JSONのみを返し、前後に説明を入れないでください:
{{
  "extracted_info": {{
    "名前": "田中太郎",
    "会社": "ABC商事",
    "課題": "デザイナー不足"
  }},
  "detected_phase": "diagnosis",
  "advice": "顧客の課題についてより深く理解するため、『デザイナー不足で具体的にどのような業務に影響が出ていますか？』と質問してみましょう。",
  "priority": "🟡",
  "suggested_response": "なるほど、デザイナー不足でお困りなんですね。具体的にはどのような場面で課題を感じられていますか？"
}}
"""
        return prompt
        
    def _parse_response(self, response_text: str) -> Dict:
        """Parse AI response into structured format"""
        try:
            # Debug: Print the raw response
            print(f"Raw Gemini response: {response_text[:200]}...")
            
            # Try to find JSON in the response
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            
            if start == -1 or end == 0:
                print("No JSON found in response")
                raise ValueError("No JSON found in response")
            
            json_str = response_text[start:end]
            print(f"Extracted JSON: {json_str[:200]}...")
            
            parsed = json.loads(json_str)
            
            # デフォルト値を設定
            return {
                "extracted_info": parsed.get("extracted_info", {}),
                "detected_phase": parsed.get("detected_phase", "diagnosis"),
                "advice": parsed.get("advice", "会話を続けて情報を収集してください"),
                "priority": parsed.get("priority", "🟢"),
                "suggested_response": parsed.get("suggested_response", "")
            }
        except Exception as e:
            print(f"Parse error: {e}")
            print(f"Full response text: {response_text}")
            
            # Re-raise the error to let the system handle it
            raise e
    
    async def generate_custom_advice(self, question: str, context: Dict) -> Dict:
        """Generate advice for custom questions"""
        recent_history = "\n".join([f"{turn['speaker']}: {turn['text']}" for turn in list(conversation_history)[-10:]])
        
        prompt = f"""
あなたは優秀な営業コンサルタントです。営業担当者からの質問に対して、現在の商談状況を踏まえた具体的なアドバイスを提供してください。

【営業担当者からの質問】
"{question}"

【事前情報】
{prior_information if prior_information else "なし"}

【現在の商談状況】
- 会話履歴:
{recent_history if recent_history else "（会話開始直後）"}

- 顧客情報:
{json.dumps(customer_profile, ensure_ascii=False) if customer_profile else "まだ収集されていません"}

- 現在のフェーズ: {current_phase}

【営業ナレッジ】
{json.dumps(knowledge['mindsets'][:2], ensure_ascii=False, indent=2)}

【タスク】
質問に対して、具体的で実践的な回答を提供してください。
- 現在の商談状況を踏まえた内容にする
- 営業マニュアルの原則に基づく
- すぐに使える具体的な提案を含める

【回答形式】
具体的で実践的な回答を提供してください。必要に応じて複数の選択肢や段階的なアプローチを提案してください。
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1024,
                    top_p=0.95,
                    top_k=64
                )
            )
        except Exception as e:
            print(f"Gemini API error in custom advice: {e}")
            raise e  # Re-raise the error to let the system handle it
        
        return {
            "question": question,
            "answer": response.text.strip(),
            "timestamp": datetime.now().isoformat()
        }

# Initialize processors
audio_processor = AudioProcessor()
stt_processor = SpeechToTextProcessor()
ai_advisor = AIAdvisor()

async def process_audio_stream():
    """Process continuous audio stream with 30-second buffering"""
    global current_phase
    
    buffer = b""
    buffer_start_time = time.time()
    buffer_duration = 30.0  # Process every 30 seconds
    min_buffer_size = 160000  # At least 10 seconds of audio
    
    continuous_transcript = ""  # Accumulate all transcripts
    last_advice_time = 0
    min_advice_interval = 30.0  # Advice every 30 seconds aligned with buffer
    
    while True:
        try:
            # Continuously collect audio data
            if not audio_queue.empty():
                audio_data = audio_queue.get()
                buffer += audio_data
            
            # Check if it's time to process (30 seconds or buffer full)
            current_time = time.time()
            time_elapsed = current_time - buffer_start_time
            
            should_process = (
                time_elapsed >= buffer_duration or
                len(buffer) >= 480000  # 30 seconds at 16kHz
            )
            
            if should_process and len(buffer) >= min_buffer_size:
                print(f"Processing {len(buffer)} bytes of audio after {time_elapsed:.1f} seconds")
                
                # Convert entire buffer to text
                transcript = await stt_processor.process_audio(buffer)
                
                if transcript and len(transcript.strip()) > 5:
                    # Add timestamp to show when this chunk was processed
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    display_text = f"[{timestamp}] {transcript}"
                    
                    # Send transcript to frontend
                    transcript_data = {
                        "type": "transcript",
                        "text": display_text,
                        "timestamp": datetime.now().isoformat()
                    }
                    advice_queue.put(transcript_data)
                    
                    # Add to conversation history (without timestamp for AI)
                    conversation_history.append({
                        "speaker": "会話",  # Just "conversation" instead of specific speaker
                        "text": transcript,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Accumulate for context
                    continuous_transcript += transcript + " "
                    
                    # Generate advice based on the continuous conversation
                    if current_time - last_advice_time >= min_advice_interval:
                        # Use recent conversation context (last 3-5 chunks)
                        recent_context = " ".join([turn["text"] for turn in list(conversation_history)[-5:]])
                        
                        advice = await ai_advisor.generate_advice(recent_context, {
                            "history": list(conversation_history),
                            "profile": customer_profile,
                            "phase": current_phase,
                            "continuous": True  # Flag for continuous conversation mode
                        })
                        
                        # Update customer profile
                        if "extracted_info" in advice:
                            customer_profile.update(advice["extracted_info"])
                        
                        # Update phase
                        if "detected_phase" in advice:
                            current_phase = advice["detected_phase"]
                        
                        # Put advice in queue
                        advice["type"] = "advice"
                        advice_queue.put(advice)
                        
                        last_advice_time = current_time
                
                # Reset buffer for next 30-second chunk
                buffer = b""
                buffer_start_time = current_time
            
            await asyncio.sleep(0.1)  # Check every 100ms
            
        except Exception as e:
            print(f"Error in audio processing: {e}")
            buffer = b""
            buffer_start_time = time.time()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await websocket.accept()
    
    # Start audio recording
    audio_processor.start_recording()
    
    # Start audio processing task
    audio_task = asyncio.create_task(process_audio_stream())
    
    try:
        while True:
            # Send advice/transcript to frontend
            if not advice_queue.empty():
                data = advice_queue.get()
                if data.get("type") == "transcript":
                    # Send transcript
                    await websocket.send_json(data)
                elif data.get("type") == "advice":
                    # Send advice
                    await websocket.send_json({
                        "type": "advice",
                        "data": data,
                        "customer_profile": customer_profile,
                        "phase": current_phase,
                        "timestamp": datetime.now().isoformat()
                    })
            
            # Check for messages from frontend
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                # Handle frontend commands
                message = json.loads(data)
                if message.get("command") == "stop":
                    audio_processor.stop_recording()
                    await websocket.send_json({"type": "status", "recording": False})
                elif message.get("command") == "start":
                    audio_processor.start_recording()
                    await websocket.send_json({"type": "status", "recording": True})
                elif message.get("command") == "question":
                    # Handle custom question
                    question = message.get("text", "")
                    custom_advice = await ai_advisor.generate_custom_advice(question, {
                        "history": list(conversation_history),
                        "profile": customer_profile,
                        "phase": current_phase
                    })
                    await websocket.send_json({
                        "type": "custom_advice",
                        "data": custom_advice,
                        "timestamp": datetime.now().isoformat()
                    })
                elif message.get("command") == "update_prior_info":
                    # Update prior information
                    global prior_information
                    prior_information = message.get("text", "")
                    await websocket.send_json({
                        "type": "prior_info_updated",
                        "status": "success"
                    })
            except asyncio.TimeoutError:
                pass
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        audio_processor.stop_recording()
        audio_task.cancel()

@app.get("/")
async def get_index():
    """Serve the main HTML page"""
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# Create HTML file
html_content = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>リアルタイム商談アドバイザー</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }
        .card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .advice-box {
            min-height: 400px;
            max-height: 600px;
            overflow-y: auto;
        }
        .advice-item {
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #ddd;
            background-color: #f9f9f9;
        }
        .advice-item.urgent {
            border-left-color: #ff4444;
            background-color: #fff5f5;
        }
        .advice-item.important {
            border-left-color: #ffaa00;
            background-color: #fffaf0;
        }
        .advice-item.normal {
            border-left-color: #00aa00;
            background-color: #f5fff5;
        }
        .phase-indicator {
            padding: 10px;
            background-color: #e3f2fd;
            border-radius: 5px;
            margin-bottom: 15px;
            text-align: center;
            font-weight: bold;
        }
        .customer-info {
            background-color: #f0f0f0;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
        }
        .status {
            padding: 10px;
            text-align: center;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        .status.connected {
            background-color: #4caf50;
            color: white;
        }
        .status.disconnected {
            background-color: #f44336;
            color: white;
        }
        .suggested-response {
            background-color: #e8f5e9;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            font-style: italic;
        }
        .control-button {
            width: 100%;
            padding: 15px;
            margin-bottom: 15px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .control-button.start {
            background-color: #4caf50;
            color: white;
        }
        .control-button.start:hover {
            background-color: #45a049;
        }
        .control-button.stop {
            background-color: #f44336;
            color: white;
        }
        .control-button.stop:hover {
            background-color: #da190b;
        }
        .control-button:disabled {
            background-color: #cccccc;
            cursor: not-allowed;
        }
        .question-input-container {
            margin-top: 20px;
            padding: 15px;
            background-color: #f0f7ff;
            border-radius: 5px;
        }
        .question-input {
            width: calc(100% - 22px);
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
            margin-bottom: 10px;
            box-sizing: border-box;
        }
        .question-button {
            width: 100%;
            padding: 10px;
            background-color: #2196F3;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }
        .question-button:hover {
            background-color: #1976D2;
        }
        .custom-advice {
            background-color: #e3f2fd;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            border-left: 4px solid #2196F3;
        }
        .quick-questions {
            margin-top: 10px;
        }
        .quick-question-btn {
            margin: 2px;
            padding: 5px 10px;
            background-color: #fff;
            border: 1px solid #2196F3;
            border-radius: 3px;
            color: #2196F3;
            cursor: pointer;
            font-size: 12px;
        }
        .quick-question-btn:hover {
            background-color: #2196F3;
            color: white;
        }
        .prior-info-container {
            margin-bottom: 20px;
            padding: 15px;
            background-color: #fff3cd;
            border-radius: 5px;
        }
        .prior-info-textarea {
            width: calc(100% - 22px);
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
            margin-bottom: 10px;
            min-height: 100px;
            resize: vertical;
            box-sizing: border-box;
        }
        .prior-info-button {
            width: 100%;
            padding: 10px;
            background-color: #ff9800;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }
        .prior-info-button:hover {
            background-color: #f57c00;
        }
        .prior-info-status {
            margin-top: 10px;
            padding: 5px;
            text-align: center;
            border-radius: 3px;
            font-size: 12px;
            display: none;
        }
        .prior-info-status.success {
            background-color: #d4edda;
            color: #155724;
            display: block;
        }
        .transcript-container {
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
            border: 1px solid #dee2e6;
        }
        .transcript-box {
            max-height: 150px;
            overflow-y: auto;
            font-size: 14px;
            line-height: 1.5;
        }
        .transcript-item {
            padding: 5px 10px;
            margin-bottom: 5px;
            background-color: white;
            border-radius: 3px;
            border-left: 3px solid #6c757d;
        }
        .transcript-item.new {
            animation: fadeIn 0.5s ease-in;
            border-left-color: #28a745;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <h1>🎯 リアルタイム商談アドバイザー</h1>
    
    <div class="container">
        <div class="card">
            <div id="status" class="status disconnected">接続中...</div>
            <button id="recordButton" class="control-button stop" onclick="toggleRecording()">
                🔴 音声入力を停止
            </button>
            <div id="phase" class="phase-indicator">フェーズ: 診断中</div>
            
            <div class="transcript-container">
                <h3>🎤 文字起こし（リアルタイム）</h3>
                <div id="transcript-box" class="transcript-box">
                    <div style="color: #6c757d; font-style: italic;">音声認識を待機中...</div>
                </div>
            </div>
            
            <h2>アドバイス</h2>
            <div id="advice-box" class="advice-box"></div>
        </div>
        
        <div class="card">
            <div class="prior-info-container">
                <h3>📋 事前情報</h3>
                <textarea id="priorInfoTextarea" class="prior-info-textarea" 
                          placeholder="顧客に関する事前情報をここに入力してください。&#10;例：&#10;- 会社名：〇〇株式会社&#10;- 業界：IT&#10;- 課題：デザイナー不足&#10;- 予算感：100万円程度&#10;- その他メモ..."></textarea>
                <button class="prior-info-button" onclick="updatePriorInfo()">事前情報を更新</button>
                <div id="priorInfoStatus" class="prior-info-status">✅ 事前情報を更新しました</div>
            </div>
            
            <h2>顧客情報</h2>
            <div id="customer-info" class="customer-info">
                <p>情報を収集中...</p>
            </div>
            
            <div class="question-input-container">
                <h3>💡 AIに質問</h3>
                <input type="text" id="questionInput" class="question-input" 
                       placeholder="例: この人へのヒアリングは何が良い？" 
                       onkeypress="if(event.key==='Enter') sendQuestion()">
                <button class="question-button" onclick="sendQuestion()">質問する</button>
                <div class="quick-questions">
                    <button class="quick-question-btn" onclick="askQuickQuestion('この顧客へのヒアリングは何が良い？')">ヒアリング提案</button>
                    <button class="quick-question-btn" onclick="askQuickQuestion('この顧客のインサイトは？')">インサイト分析</button>
                    <button class="quick-question-btn" onclick="askQuickQuestion('次に聞くべき質問は？')">次の質問</button>
                    <button class="quick-question-btn" onclick="askQuickQuestion('クロージングのタイミングは？')">クロージング</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let isRecording = true;
        
        function connectWebSocket() {
            ws = new WebSocket('ws://localhost:8001/ws');
            
            ws.onopen = function() {
                document.getElementById('status').className = 'status connected';
                document.getElementById('status').textContent = '🟢 接続中 - 音声を分析しています';
                updateRecordButton(true);
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                
                if (data.type === 'advice') {
                    // Update phase
                    document.getElementById('phase').textContent = 
                        `フェーズ: ${getPhaseLabel(data.phase)}`;
                    
                    // Add advice
                    addAdvice(data.data);
                    
                    // Update customer profile
                    updateCustomerInfo(data.customer_profile);
                } else if (data.type === 'status') {
                    isRecording = data.recording;
                    updateRecordButton(data.recording);
                } else if (data.type === 'custom_advice') {
                    // Add custom advice response
                    addCustomAdvice(data.data);
                } else if (data.type === 'prior_info_updated') {
                    // Show success message
                    const status = document.getElementById('priorInfoStatus');
                    status.className = 'prior-info-status success';
                    setTimeout(() => {
                        status.className = 'prior-info-status';
                    }, 3000);
                } else if (data.type === 'transcript') {
                    // Add transcript
                    addTranscript(data.text);
                }
            };
            
            ws.onclose = function() {
                document.getElementById('status').className = 'status disconnected';
                document.getElementById('status').textContent = '❌ 切断されました - 再接続中...';
                setTimeout(connectWebSocket, 3000);
            };
        }
        
        function toggleRecording() {
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                alert('WebSocket接続が確立されていません');
                return;
            }
            
            if (isRecording) {
                ws.send(JSON.stringify({ command: 'stop' }));
            } else {
                ws.send(JSON.stringify({ command: 'start' }));
            }
        }
        
        function updateRecordButton(recording) {
            const button = document.getElementById('recordButton');
            if (recording) {
                button.textContent = '🔴 音声入力を停止';
                button.className = 'control-button stop';
            } else {
                button.textContent = '🎤 音声入力を開始';
                button.className = 'control-button start';
            }
        }
        
        function getPhaseLabel(phase) {
            const labels = {
                'diagnosis': '診断',
                'redefinition': '再定義',
                'future_presentation': '未来提示',
                'decision_facilitation': '決断促進'
            };
            return labels[phase] || phase;
        }
        
        function addAdvice(advice) {
            const adviceBox = document.getElementById('advice-box');
            const adviceItem = document.createElement('div');
            
            const priorityClass = advice.priority === '🔴' ? 'urgent' : 
                                advice.priority === '🟡' ? 'important' : 'normal';
            
            adviceItem.className = `advice-item ${priorityClass}`;
            adviceItem.innerHTML = `
                <div><strong>${advice.priority} アドバイス:</strong></div>
                <div>${advice.advice}</div>
                ${advice.suggested_response ? 
                    `<div class="suggested-response">💡 提案する返答: ${advice.suggested_response}</div>` : ''}
            `;
            
            adviceBox.insertBefore(adviceItem, adviceBox.firstChild);
            
            // Keep only last 10 advice items
            while (adviceBox.children.length > 10) {
                adviceBox.removeChild(adviceBox.lastChild);
            }
        }
        
        function updateCustomerInfo(profile) {
            const infoDiv = document.getElementById('customer-info');
            let html = '';
            
            for (const [key, value] of Object.entries(profile)) {
                const label = getProfileLabel(key);
                html += `<p><strong>${label}:</strong> ${value}</p>`;
            }
            
            if (html === '') {
                html = '<p>情報を収集中...</p>';
            }
            
            infoDiv.innerHTML = html;
        }
        
        function getProfileLabel(key) {
            const labels = {
                'name': '名前',
                'company': '会社',
                'role': '役職',
                'challenge': '課題',
                'budget': '予算',
                'timeline': '期限',
                'motivation': '動機',
                'concerns': '懸念事項'
            };
            return labels[key] || key;
        }
        
        function sendQuestion() {
            const input = document.getElementById('questionInput');
            const question = input.value.trim();
            
            if (!question) return;
            
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                alert('WebSocket接続が確立されていません');
                return;
            }
            
            ws.send(JSON.stringify({ 
                command: 'question',
                text: question 
            }));
            
            input.value = '';
        }
        
        function askQuickQuestion(question) {
            document.getElementById('questionInput').value = question;
            sendQuestion();
        }
        
        function addCustomAdvice(data) {
            const adviceBox = document.getElementById('advice-box');
            const adviceItem = document.createElement('div');
            adviceItem.className = 'custom-advice';
            adviceItem.innerHTML = `
                <div><strong>💡 質問:</strong> ${data.question}</div>
                <div style="margin-top: 10px;"><strong>回答:</strong></div>
                <div>${data.answer}</div>
            `;
            
            adviceBox.insertBefore(adviceItem, adviceBox.firstChild);
            
            // Keep only last 10 items
            while (adviceBox.children.length > 10) {
                adviceBox.removeChild(adviceBox.lastChild);
            }
        }
        
        function updatePriorInfo() {
            const textarea = document.getElementById('priorInfoTextarea');
            const priorInfo = textarea.value.trim();
            
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                alert('WebSocket接続が確立されていません');
                return;
            }
            
            ws.send(JSON.stringify({ 
                command: 'update_prior_info',
                text: priorInfo 
            }));
        }
        
        function addTranscript(text) {
            const transcriptBox = document.getElementById('transcript-box');
            
            // Remove initial message if present
            if (transcriptBox.innerHTML.includes('音声認識を待機中')) {
                transcriptBox.innerHTML = '';
            }
            
            const transcriptItem = document.createElement('div');
            transcriptItem.className = 'transcript-item new';
            transcriptItem.textContent = text;
            
            transcriptBox.appendChild(transcriptItem);
            
            // Auto scroll to bottom
            transcriptBox.scrollTop = transcriptBox.scrollHeight;
            
            // Remove 'new' class after animation
            setTimeout(() => {
                transcriptItem.classList.remove('new');
            }, 500);
            
            // Keep only last 10 transcripts
            while (transcriptBox.children.length > 10) {
                transcriptBox.removeChild(transcriptBox.firstChild);
            }
        }
        
        
        // Connect on page load
        connectWebSocket();
    </script>
</body>
</html>"""

# Write HTML file
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

if __name__ == "__main__":
    print("リアルタイム商談アドバイザーを起動しています...")
    print("ブラウザで http://localhost:8001 にアクセスしてください")
    uvicorn.run(app, host="127.0.0.1", port=8001)
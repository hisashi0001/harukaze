import { OpenAI } from 'openai';
import guidelines from '../data/guidelines.json';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// CORSヘッダーを設定
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

export default async function handler(req, res) {
  // CORS対応
  if (req.method === 'OPTIONS') {
    return res.status(200).json({});
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { message } = req.body;
    
    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // ユーザーの質問に関連するガイドラインを検索
    const relevantGuidelines = findRelevantGuidelines(message);
    
    // コンテキストを構築
    const context = buildContext(relevantGuidelines);
    
    // OpenAI APIを呼び出し
    const completion = await openai.chat.completions.create({
      model: 'gpt-3.5-turbo',
      messages: [
        {
          role: 'system',
          content: `あなたはHarukazeガイドラインのAIアシスタントです。
以下のガイドライン情報を基に、ユーザーの質問に的確に答えてください。
回答は具体的で実践的なアドバイスを心がけ、関連するページがあれば必ず紹介してください。

利用可能なガイドライン情報:
${context}

回答形式:
1. 質問に対する直接的な回答
2. 具体的な実践方法やポイント
3. 「詳しくは〇〇ページをご覧ください」という形で関連ページを紹介`
        },
        {
          role: 'user',
          content: message
        }
      ],
      temperature: 0.7,
      max_tokens: 800,
    });

    const response = completion.choices[0].message.content;
    
    // 関連ページ情報を追加
    const relatedPages = relevantGuidelines.slice(0, 3).map(g => ({
      title: g.title,
      url: g.url,
      category: g.category
    }));

    res.status(200).json({
      response,
      relatedPages,
      success: true
    });

  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
}

// 関連するガイドラインを検索
function findRelevantGuidelines(query) {
  const queryLower = query.toLowerCase();
  const scores = [];

  guidelines.forEach(guideline => {
    let score = 0;
    
    // タイトルに含まれる場合は高スコア
    if (guideline.title.toLowerCase().includes(queryLower)) {
      score += 10;
    }
    
    // キーワードマッチング
    guideline.keywords.forEach(keyword => {
      if (queryLower.includes(keyword) || keyword.includes(queryLower)) {
        score += 5;
      }
    });
    
    // コンテンツに含まれる場合
    const contentMatches = (guideline.content.toLowerCase().match(new RegExp(queryLower, 'g')) || []).length;
    score += contentMatches * 0.5;
    
    // カテゴリマッチング
    if (guideline.category && queryLower.includes(guideline.category.toLowerCase())) {
      score += 3;
    }
    
    if (score > 0) {
      scores.push({ guideline, score });
    }
  });

  // スコアの高い順にソート
  scores.sort((a, b) => b.score - a.score);
  
  return scores.slice(0, 5).map(s => s.guideline);
}

// コンテキストを構築
function buildContext(guidelines) {
  if (guidelines.length === 0) {
    return 'ガイドラインに関連する情報が見つかりませんでした。';
  }

  return guidelines.map(g => {
    const excerpt = g.summary.substring(0, 200) + '...';
    return `
【${g.title}】（${g.category}）
${excerpt}
URL: ${g.url}
`;
  }).join('\n---\n');
}
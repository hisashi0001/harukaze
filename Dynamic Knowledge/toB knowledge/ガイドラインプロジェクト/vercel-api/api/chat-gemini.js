const { GoogleGenerativeAI } = require('@google/generative-ai');

module.exports = async function handler(req, res) {
  // CORSヘッダーを設定
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  // CORS対応
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // ガイドラインデータを安全に読み込む
    let guidelines = [];
    try {
      guidelines = require('./guidelines-data.js');
    } catch (loadError) {
      console.error('Failed to load guidelines data:', loadError);
      // ガイドラインが読み込めなくても続行
    }
    
    const { message } = req.body;
    
    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Gemini APIクライアントを初期化
    const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
    const model = genAI.getGenerativeModel({ model: 'gemini-2.5-flash' });

    // ユーザーの質問に関連するガイドラインを検索
    const relevantGuidelines = findRelevantGuidelines(message, guidelines);
    
    // 関連が薄くても全体的な情報を含める
    if (relevantGuidelines.length < 5 && guidelines.length > 0) {
      // ランダムに追加のガイドラインを含める
      const additionalGuidelines = guidelines
        .filter(g => !relevantGuidelines.includes(g))
        .slice(0, 5 - relevantGuidelines.length);
      relevantGuidelines.push(...additionalGuidelines);
    }
    
    // コンテキストを構築
    const context = buildContext(relevantGuidelines);
    
    // プロンプトを構築
    const prompt = `あなたはHarukazeガイドラインのAIアシスタントです。HarukazeはtoB事業としてデザイン制作を行っているクリエイティブチームです。

以下のガイドライン情報を参考に、ユーザーの質問に答えてください：
${context}

ユーザーの質問: ${message}

回答は2-3文程度で簡潔に。ガイドラインからの情報を優先し、ない場合は一般的な知識で答えてください。`;

    // Gemini APIを呼び出し
    const result = await model.generateContent(prompt);
    const response = result.response.text();
    
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
    console.error('Gemini API Error:', error);
    
    // エラー時は簡易回答にフォールバック
    const fallbackResponse = generateSimpleResponse(message || '');
    
    res.status(200).json({
      response: fallbackResponse + '\n\n（注: AIによる詳細な回答機能に一時的な問題が発生しています）',
      relatedPages: [],
      success: true
    });
  }
}

// 関連するガイドラインを検索
function findRelevantGuidelines(query, guidelines) {
  if (!guidelines || guidelines.length === 0) {
    return [];
  }
  
  const queryLower = query.toLowerCase();
  const scores = [];

  guidelines.forEach(guideline => {
    let score = 0;
    
    // タイトルに含まれる場合は高スコア
    if (guideline.title && guideline.title.toLowerCase().includes(queryLower)) {
      score += 10;
    }
    
    // キーワードマッチング
    if (guideline.keywords && Array.isArray(guideline.keywords)) {
      guideline.keywords.forEach(keyword => {
        if (queryLower.includes(keyword) || keyword.includes(queryLower)) {
          score += 5;
        }
      });
    }
    
    // コンテンツに含まれる場合（より重要度を上げる）
    if (guideline.content) {
      const contentLower = guideline.content.toLowerCase();
      // 完全一致は高スコア
      if (contentLower.includes(queryLower)) {
        score += 8;
      }
      // 部分一致も評価
      const queryWords = queryLower.split(/\s+/);
      queryWords.forEach(word => {
        if (word.length > 2 && contentLower.includes(word)) {
          score += 2;
        }
      });
    }
    
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
  
  return scores.slice(0, 10).map(s => s.guideline);
}

// コンテキストを構築
function buildContext(guidelines) {
  if (!guidelines || guidelines.length === 0) {
    return 'ガイドラインに関連する情報が見つかりませんでした。';
  }

  // より多くのコンテンツ情報を含める
  return guidelines.map(g => {
    // contentとsummaryの両方を使用し、より多くの情報を提供
    const content = g.content || g.summary || '';
    const excerpt = content.substring(0, 500) + (content.length > 500 ? '...' : '');
    return `
【${g.title}】（${g.category || '未分類'}）
${excerpt}
`;
  }).join('\n\n');
}

// 簡易的な回答生成（フォールバック用）
function generateSimpleResponse(query) {
  const responses = {
    '納期': '納期が遅れそうな場合は、早めにクライアントに連絡し、代替案を提示することが大切です。',
    'フィードバック': '効果的なフィードバックは具体的で建設的に行い、改善点を明確に伝えることが重要です。',
    'デザイナー': 'デザイナーの強みを理解し、適材適所のアサインと成長機会の提供が大切です。',
    '品質': '品質チェックはラフ段階、完成段階、納品前の3段階で行うことが重要です。',
    '商談': '商談では相手のニーズを深く理解し、Win-Winの関係を構築することが大切です。'
  };
  
  for (const [key, response] of Object.entries(responses)) {
    if (query.includes(key)) {
      return response;
    }
  }
  
  return `${query}についてお答えします。一般的には、相手の立場を理解し、明確なコミュニケーションを心がけることが重要です。`;
}
デザジュクではAIのカリキュラムをすでに始動しており、デザインスクールとしての訴求方法もAIに寄せていける。
AIによってほぼ自動でデザインが完成するシステムも構築しており、競合優位性につながると考えている。

ーーー
AIの市場リサーチは以下の2つのファイルを参照
/Users/ogatahisashi/Library/CloudStorage/GoogleDrive-harukazeteam01@gmail.com/My Drive/HarukazeDatabase/Dynamic Knowledge/Hisashi's personal folder/事業計画書プロジェクト/参考資料/市場リサーチ/AI市場リサーチClaude.md

/Users/ogatahisashi/Library/CloudStorage/GoogleDrive-harukazeteam01@gmail.com/My Drive/HarukazeDatabase/Dynamic Knowledge/Hisashi's personal folder/事業計画書プロジェクト/参考資料/市場リサーチ/AI市場リサーチGemini.md
ーーー

市場規模の増加を示したグラフ用コード↓

import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area, BarChart, Bar } from 'recharts';

export default function AIMarketCharts() {
  const [chartType, setChartType] = useState('line');

  // グローバル市場データ（中央値を使用）
  const globalData = [
    { year: 2015, value: 85 },
    { year: 2016, value: 105 },
    { year: 2017, value: 135 },
    { year: 2018, value: 175 },
    { year: 2019, value: 225 },
    { year: 2020, value: 275 },
    { year: 2021, value: 375 },
    { year: 2022, value: 550 },
    { year: 2023, value: 1450 },
    { year: 2024, value: 2300 },
    { year: 2025, value: 3750 },
    { year: 2026, value: 5000 },
    { year: 2027, value: 6750 },
    { year: 2028, value: 9000 },
    { year: 2029, value: 11000 },
    { year: 2030, value: 14000 },
    { year: 2031, value: 18500 },
    { year: 2032, value: 24500 },
    { year: 2033, value: 31500 },
    { year: 2034, value: 39000 },
    { year: 2035, value: 47500 }
  ];

  // 日本市場データ（中央値を使用、億円）
  const japanData = [
    { year: 2015, value: 1250 },
    { year: 2016, value: 1958 },
    { year: 2017, value: 2568 },
    { year: 2018, value: 5301 },
    { year: 2019, value: 3935 },
    { year: 2020, value: 10000 },
    { year: 2021, value: 2866 },
    { year: 2022, value: 3884 },
    { year: 2023, value: 6859 },
    { year: 2024, value: 9001 },
    { year: 2025, value: 14000 },
    { year: 2026, value: 17500 },
    { year: 2027, value: 21500 },
    { year: 2028, value: 26607 },
    { year: 2029, value: 32500 },
    { year: 2030, value: 39000 },
    { year: 2031, value: 46500 },
    { year: 2032, value: 55500 },
    { year: 2033, value: 65500 },
    { year: 2034, value: 76500 },
    { year: 2035, value: 88500 }
  ];

  // 統合データ（比較用）
  const combinedData = globalData.map((item, index) => ({
    year: item.year,
    global: item.value,
    japan: japanData[index].value / 100 // 億円をドル換算（1ドル=100円で計算）
  }));

  // カスタムツールチップ
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold">{`${label}年`}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: {entry.value.toLocaleString()} {entry.name === '日本' ? '億円' : '億ドル'}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  // Y軸のフォーマット
  const formatYAxis = (value) => {
    if (value >= 10000) {
      return `${(value / 10000).toFixed(1)}兆`;
    }
    return `${value.toLocaleString()}`;
  };

  return (
    <div className="w-full p-6 bg-gray-50">
      <h1 className="text-3xl font-bold text-center mb-8 text-gray-800">
        AI市場規模推移（2015-2035年）
      </h1>

      {/* チャートタイプ選択 */}
      <div className="flex justify-center mb-6 space-x-4">
        <button
          onClick={() => setChartType('line')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            chartType === 'line' 
              ? 'bg-blue-600 text-white' 
              : 'bg-white text-gray-700 hover:bg-gray-100'
          }`}
        >
          折れ線グラフ
        </button>
        <button
          onClick={() => setChartType('area')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            chartType === 'area' 
              ? 'bg-blue-600 text-white' 
              : 'bg-white text-gray-700 hover:bg-gray-100'
          }`}
        >
          エリアチャート
        </button>
        <button
          onClick={() => setChartType('bar')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            chartType === 'bar' 
              ? 'bg-blue-600 text-white' 
              : 'bg-white text-gray-700 hover:bg-gray-100'
          }`}
        >
          棒グラフ
        </button>
      </div>

      {/* グローバル市場グラフ */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <h2 className="text-2xl font-semibold mb-4 text-gray-700">
          グローバルAI市場規模（億ドル）
        </h2>
        <ResponsiveContainer width="100%" height={400}>
          {chartType === 'line' ? (
            <LineChart data={globalData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis dataKey="year" stroke="#666" />
              <YAxis tickFormatter={formatYAxis} stroke="#666" />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke="#3b82f6" 
                strokeWidth={3}
                dot={{ fill: '#3b82f6', r: 4 }}
                activeDot={{ r: 6 }}
                name="グローバル"
              />
            </LineChart>
          ) : chartType === 'area' ? (
            <AreaChart data={globalData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis dataKey="year" stroke="#666" />
              <YAxis tickFormatter={formatYAxis} stroke="#666" />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Area 
                type="monotone" 
                dataKey="value" 
                stroke="#3b82f6" 
                fill="#93c5fd"
                strokeWidth={2}
                name="グローバル"
              />
            </AreaChart>
          ) : (
            <BarChart data={globalData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis dataKey="year" stroke="#666" />
              <YAxis tickFormatter={formatYAxis} stroke="#666" />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Bar dataKey="value" fill="#3b82f6" name="グローバル" />
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>

      {/* 日本市場グラフ */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <h2 className="text-2xl font-semibold mb-4 text-gray-700">
          日本AI市場規模（億円）
        </h2>
        <ResponsiveContainer width="100%" height={400}>
          {chartType === 'line' ? (
            <LineChart data={japanData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis dataKey="year" stroke="#666" />
              <YAxis tickFormatter={formatYAxis} stroke="#666" />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke="#ef4444" 
                strokeWidth={3}
                dot={{ fill: '#ef4444', r: 4 }}
                activeDot={{ r: 6 }}
                name="日本"
              />
            </LineChart>
          ) : chartType === 'area' ? (
            <AreaChart data={japanData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis dataKey="year" stroke="#666" />
              <YAxis tickFormatter={formatYAxis} stroke="#666" />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Area 
                type="monotone" 
                dataKey="value" 
                stroke="#ef4444" 
                fill="#fca5a5"
                strokeWidth={2}
                name="日本"
              />
            </AreaChart>
          ) : (
            <BarChart data={japanData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis dataKey="year" stroke="#666" />
              <YAxis tickFormatter={formatYAxis} stroke="#666" />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Bar dataKey="value" fill="#ef4444" name="日本" />
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>

      {/* 比較グラフ */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-semibold mb-4 text-gray-700">
          日本・グローバル市場比較（億ドル換算）
        </h2>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={combinedData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis dataKey="year" stroke="#666" />
            <YAxis tickFormatter={formatYAxis} stroke="#666" />
            <Tooltip 
              content={({ active, payload, label }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
                      <p className="font-semibold">{`${label}年`}</p>
                      {payload.map((entry, index) => (
                        <p key={index} style={{ color: entry.color }}>
                          {entry.name}: {entry.value.toLocaleString()} 億ドル
                        </p>
                      ))}
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="global" 
              stroke="#3b82f6" 
              strokeWidth={3}
              dot={{ fill: '#3b82f6', r: 4 }}
              name="グローバル"
            />
            <Line 
              type="monotone" 
              dataKey="japan" 
              stroke="#ef4444" 
              strokeWidth={3}
              dot={{ fill: '#ef4444', r: 4 }}
              name="日本（ドル換算）"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* 市場成長率 */}
      <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-semibold mb-4 text-gray-700">
          主要ポイント
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-semibold text-blue-800 mb-2">グローバル市場</h3>
            <ul className="space-y-1 text-sm text-gray-700">
              <li>• 2023年のChatGPT登場で急成長</li>
              <li>• 2024年: 2,300億ドル</li>
              <li>• 2030年: 1.4兆ドル（予測）</li>
              <li>• 2035年: 4.75兆ドル（予測）</li>
              <li>• CAGR: 約30-37%（2024-2035）</li>
            </ul>
          </div>
          <div className="bg-red-50 p-4 rounded-lg">
            <h3 className="font-semibold text-red-800 mb-2">日本市場</h3>
            <ul className="space-y-1 text-sm text-gray-700">
              <li>• 生成AIが市場拡大を牽引</li>
              <li>• 2024年: 9,001億円</li>
              <li>• 2030年: 3.9兆円（予測）</li>
              <li>• 2035年: 8.85兆円（予測）</li>
              <li>• CAGR: 約20-25%（2024-2035）</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
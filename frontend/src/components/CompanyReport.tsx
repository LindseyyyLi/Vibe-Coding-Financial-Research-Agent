import React from 'react';
import { CompanyData } from '../services/api';

interface CompanyReportProps {
    data: CompanyData;
}

const formatNumber = (value: string | number): string => {
    if (typeof value === 'number') {
        return new Intl.NumberFormat('en-US', {
            style: 'decimal',
            maximumFractionDigits: 2
        }).format(value);
    }
    return value === 'N/A' ? 'N/A' : formatNumber(parseFloat(value));
};

const CompanyReport: React.FC<CompanyReportProps> = ({ data }) => {
    return (
        <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-2xl font-bold mb-4">{data.company_info.name}</h2>
            
            <section className="mb-6">
                <h3 className="text-xl font-semibold mb-2">Company Overview</h3>
                <p className="text-gray-700 mb-4">{data.company_info.description}</p>
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <span className="font-medium">Sector: </span>
                        <span className="text-gray-700">{data.company_info.sector}</span>
                    </div>
                    <div>
                        <span className="font-medium">Industry: </span>
                        <span className="text-gray-700">{data.company_info.industry}</span>
                    </div>
                </div>
            </section>

            <section className="mb-6">
                <h3 className="text-xl font-semibold mb-2">Market Data</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="border rounded p-3">
                        <div className="text-sm text-gray-600">Current Price</div>
                        <div className="font-medium text-lg">
                            ${formatNumber(data.financial_data.price)}
                            <span className={`ml-2 text-sm ${
                                parseFloat(data.financial_data.change_percent) >= 0 
                                ? 'text-green-600' 
                                : 'text-red-600'}`}>
                                ({formatNumber(data.financial_data.change_percent)}%)
                            </span>
                        </div>
                    </div>
                    <div className="border rounded p-3">
                        <div className="text-sm text-gray-600">Market Cap</div>
                        <div className="font-medium">{formatNumber(data.financial_data.market_cap)}</div>
                    </div>
                    <div className="border rounded p-3">
                        <div className="text-sm text-gray-600">Volume</div>
                        <div className="font-medium">{formatNumber(data.financial_data.volume)}</div>
                    </div>
                    <div className="border rounded p-3">
                        <div className="text-sm text-gray-600">52 Week Range</div>
                        <div className="font-medium">
                            ${formatNumber(data.financial_data.week_52_low)} - ${formatNumber(data.financial_data.week_52_high)}
                        </div>
                    </div>
                </div>
            </section>

            <section className="mb-6">
                <h3 className="text-xl font-semibold mb-2">Financial Metrics</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="border rounded p-3">
                        <div className="text-sm text-gray-600">Revenue (TTM)</div>
                        <div className="font-medium">${formatNumber(data.financial_data.revenue)}</div>
                    </div>
                    <div className="border rounded p-3">
                        <div className="text-sm text-gray-600">Gross Profit</div>
                        <div className="font-medium">${formatNumber(data.financial_data.gross_profit)}</div>
                    </div>
                    <div className="border rounded p-3">
                        <div className="text-sm text-gray-600">Operating Income</div>
                        <div className="font-medium">${formatNumber(data.financial_data.operatingIncome)}</div>
                    </div>
                    <div className="border rounded p-3">
                        <div className="text-sm text-gray-600">Net Income</div>
                        <div className="font-medium">${formatNumber(data.financial_data.netIncome)}</div>
                    </div>
                    <div className="border rounded p-3">
                        <div className="text-sm text-gray-600">EPS</div>
                        <div className="font-medium">${formatNumber(data.financial_data.EPS)}</div>
                    </div>
                    <div className="border rounded p-3">
                        <div className="text-sm text-gray-600">P/E Ratio</div>
                        <div className="font-medium">{formatNumber(data.financial_data.pe_ratio)}</div>
                    </div>
                    <div className="border rounded p-3">
                        <div className="text-sm text-gray-600">Operating Margin</div>
                        <div className="font-medium">{formatNumber(data.financial_data.operating_margin)}%</div>
                    </div>
                    <div className="border rounded p-3">
                        <div className="text-sm text-gray-600">ROE</div>
                        <div className="font-medium">{formatNumber(data.financial_data.ReturnOnEquityTTM)}%</div>
                    </div>
                    <div className="border rounded p-3">
                        <div className="text-sm text-gray-600">ROA</div>
                        <div className="font-medium">{formatNumber(data.financial_data.ReturnOnAssetsTTM)}%</div>
                    </div>
                </div>
            </section>

            <section className="mb-6">
                <h3 className="text-xl font-semibold mb-2">Growth & Analysis</h3>
                <div className="space-y-4">
                    <div className="border rounded p-4">
                        <h4 className="font-medium mb-2">Financial Health</h4>
                        <p className="text-gray-700">{data.financial_analysis.financial_health}</p>
                    </div>
                    <div className="border rounded p-4">
                        <h4 className="font-medium mb-2">Market Position</h4>
                        <p className="text-gray-700">{data.financial_analysis.market_position}</p>
                    </div>
                    <div className="border rounded p-4">
                        <h4 className="font-medium mb-2">Growth Potential</h4>
                        <p className="text-gray-700">{data.financial_analysis.growth_potential}</p>
                    </div>
                    <div className="border rounded p-4">
                        <h4 className="font-medium mb-2">Key Metrics Analysis</h4>
                        <p className="text-gray-700">{data.financial_analysis.key_metrics_analysis}</p>
                    </div>
                </div>
            </section>
            
            <section className="mb-6">
                <h3 className="text-xl font-semibold mb-2">Potential Risks</h3>
                <ul className="list-disc list-inside space-y-2">
                    {data.potential_risks.map((risk, index) => (
                        <li key={index} className="text-gray-700">{risk}</li>
                    ))}
                </ul>
            </section>
            
            <section>
                <h3 className="text-xl font-semibold mb-2">Recent News</h3>
                <div className="space-y-4">
                    {data.news_data.map((news, index) => (
                        <div key={index} className="border rounded p-4">
                            <h4 className="font-medium mb-2">
                                <a 
                                    href={news.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-blue-600 hover:text-blue-800"
                                >
                                    {news.title}
                                </a>
                            </h4>
                            <p className="text-gray-700 text-sm">{news.description}</p>
                            <p className="text-gray-500 text-xs mt-2">
                                {new Date(news.publishedAt).toLocaleDateString()}
                            </p>
                        </div>
                    ))}
                </div>
            </section>
        </div>
    );
};

export default CompanyReport; 
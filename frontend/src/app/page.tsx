'use client';

import { useState } from 'react';
import CompanySearch from '../components/CompanySearch';
import CompanyReport from '../components/CompanyReport';

interface CompanyData {
    company_name: string;
    overview: string;
    financial_metrics: {
        [key: string]: any;
    };
    potential_risks: string[];
    sources: string[];
}

export default function Home() {
    const [companyData, setCompanyData] = useState<CompanyData | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleResult = (data: CompanyData) => {
        setError(null);
        setCompanyData(data);
    };

    const handleError = (errorMessage: string) => {
        setError(errorMessage);
        setCompanyData(null);
    };

    return (
        <main className="min-h-screen p-8">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-3xl font-bold text-center mb-8">
                    Financial Research Assistant
                </h1>
                
                <CompanySearch onResult={handleResult} onError={handleError} />
                
                {error && (
                    <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
                        {error}
                    </div>
                )}
                
                {companyData && (
                    <div className="mt-8">
                        <CompanyReport data={companyData} />
                    </div>
                )}
            </div>
        </main>
    );
} 
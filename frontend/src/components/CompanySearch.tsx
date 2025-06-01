import React, { useState } from 'react';
import { analyzeCompany, CompanyData } from '../services/api';

interface CompanySearchProps {
    onResult: (data: CompanyData) => void;
    onError: (error: string) => void;
}

const CompanySearch: React.FC<CompanySearchProps> = ({ onResult, onError }) => {
    const [companyName, setCompanyName] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [inputError, setInputError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setInputError(null);
        
        const trimmedName = companyName.trim();
        if (!trimmedName) {
            setInputError('Please enter a company name');
            onError('Please enter a company name');
            return;
        }

        setIsLoading(true);
        try {
            console.log('Submitting company search for:', trimmedName);
            const result = await analyzeCompany(trimmedName);
            console.log('Search result:', result);
            onResult(result);
        } catch (error) {
            console.error('Search error:', error);
            const errorMessage = error instanceof Error ? error.message : 'Failed to analyze company';
            onError(errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="w-full max-w-md mx-auto p-4">
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label htmlFor="companyName" className="block text-sm font-medium text-gray-700">
                        Company Name
                    </label>
                    <input
                        type="text"
                        id="companyName"
                        value={companyName}
                        onChange={(e) => {
                            setCompanyName(e.target.value);
                            setInputError(null);
                        }}
                        placeholder="Enter company name (e.g., Tesla, Apple, Microsoft)"
                        className={`mt-1 block w-full rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 ${
                            inputError 
                                ? 'border-red-300 text-red-900 placeholder-red-300'
                                : 'border-gray-300'
                        }`}
                        disabled={isLoading}
                    />
                    {inputError && (
                        <p className="mt-2 text-sm text-red-600">
                            {inputError}
                        </p>
                    )}
                </div>
                <button
                    type="submit"
                    disabled={isLoading}
                    className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
                        isLoading 
                            ? 'bg-blue-400 cursor-not-allowed' 
                            : 'bg-blue-600 hover:bg-blue-700'
                    } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
                >
                    {isLoading ? (
                        <>
                            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Analyzing...
                        </>
                    ) : 'Analyze Company'}
                </button>
            </form>
        </div>
    );
};

export default CompanySearch; 
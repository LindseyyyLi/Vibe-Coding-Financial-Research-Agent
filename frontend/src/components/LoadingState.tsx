export default function LoadingState() {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
      <p className="ml-4 text-lg text-gray-600">Analyzing company data...</p>
    </div>
  );
} 
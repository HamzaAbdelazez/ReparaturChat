import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github.css'; // You can choose different themes

const MarkdownRenderer = ({ content, className = "" }) => {
  const components = {
    // Custom styling for different markdown elements
    h1: ({ node, ...props }) => (
      <h1 className="text-2xl font-bold text-gray-900 mb-4 mt-6 first:mt-0" {...props} />
    ),
    h2: ({ node, ...props }) => (
      <h2 className="text-xl font-semibold text-gray-800 mb-3 mt-5 first:mt-0" {...props} />
    ),
    h3: ({ node, ...props }) => (
      <h3 className="text-lg font-medium text-gray-800 mb-2 mt-4 first:mt-0" {...props} />
    ),
    h4: ({ node, ...props }) => (
      <h4 className="text-base font-medium text-gray-700 mb-2 mt-3 first:mt-0" {...props} />
    ),
    h5: ({ node, ...props }) => (
      <h5 className="text-sm font-medium text-gray-700 mb-1 mt-2 first:mt-0" {...props} />
    ),
    h6: ({ node, ...props }) => (
      <h6 className="text-sm font-medium text-gray-600 mb-1 mt-2 first:mt-0" {...props} />
    ),
    p: ({ node, ...props }) => (
      <p className="text-gray-800 mb-3 leading-relaxed" {...props} />
    ),
    ul: ({ node, ...props }) => (
      <ul className="list-disc list-inside ml-4 mb-3 space-y-1 text-gray-800" {...props} />
    ),
    ol: ({ node, ...props }) => (
      <ol className="list-decimal list-inside ml-4 mb-3 space-y-1 text-gray-800" {...props} />
    ),
    li: ({ node, ...props }) => (
      <li className="leading-relaxed" {...props} />
    ),
    blockquote: ({ node, ...props }) => (
      <blockquote className="border-l-4 border-blue-500 bg-blue-50 pl-4 py-2 my-3 italic text-blue-900" {...props} />
    ),
    code: ({ node, inline, ...props }) => {
      if (inline) {
        return (
          <code className="bg-gray-100 text-red-600 px-1.5 py-0.5 rounded text-sm font-mono" {...props} />
        );
      }
      return (
        <code className="block bg-gray-900 text-gray-100 p-4 rounded-lg text-sm font-mono overflow-x-auto my-3" {...props} />
      );
    },
    pre: ({ node, ...props }) => (
      <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg text-sm font-mono overflow-x-auto my-3" {...props} />
    ),
    table: ({ node, ...props }) => (
      <div className="overflow-x-auto my-3">
        <table className="min-w-full border-collapse border border-gray-300" {...props} />
      </div>
    ),
    thead: ({ node, ...props }) => (
      <thead className="bg-gray-50" {...props} />
    ),
    th: ({ node, ...props }) => (
      <th className="border border-gray-300 px-4 py-2 text-left font-semibold text-gray-900" {...props} />
    ),
    td: ({ node, ...props }) => (
      <td className="border border-gray-300 px-4 py-2 text-gray-800" {...props} />
    ),
    tr: ({ node, ...props }) => (
      <tr className="even:bg-gray-50" {...props} />
    ),
    strong: ({ node, ...props }) => (
      <strong className="font-bold text-gray-900" {...props} />
    ),
    em: ({ node, ...props }) => (
      <em className="italic text-gray-800" {...props} />
    ),
    a: ({ node, ...props }) => (
      <a 
        className="text-blue-600 hover:text-blue-800 underline" 
        target="_blank" 
        rel="noopener noreferrer" 
        {...props} 
      />
    ),
    hr: ({ node, ...props }) => (
      <hr className="border-t border-gray-300 my-6" {...props} />
    ),
    // Special styling for repair-specific elements
    div: ({ node, className: divClassName, ...props }) => {
      // Add special styling for safety warnings or important notes
      if (divClassName?.includes('warning')) {
        return (
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 my-3" {...props} />
        );
      }
      if (divClassName?.includes('danger')) {
        return (
          <div className="bg-red-50 border-l-4 border-red-400 p-4 my-3" {...props} />
        );
      }
      if (divClassName?.includes('info')) {
        return (
          <div className="bg-blue-50 border-l-4 border-blue-400 p-4 my-3" {...props} />
        );
      }
      return <div {...props} />;
    }
  };

  return (
    <div className={`markdown-content ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkBreaks]}
        rehypePlugins={[rehypeHighlight]}
        components={components}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownRenderer;
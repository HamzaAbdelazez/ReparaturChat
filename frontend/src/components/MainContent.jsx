import React from "react";
import { useTranslation } from "react-i18next";
import DocumentUpload from "./DocumentUpload";
import ToolAnalysis from "./ToolAnalysis";
import DeviceSelector from "./DeviceSelector";
import RepairAnalysis from "./RepairAnalysis";
import ChatInterface from "./ChatInterface";
import LLMModelSelector from "./LLMModelSelector";
import LanguageSwitcher from "./LanguageSwitcher";

function MainContent({
  // PDF related
  file,
  uploadStatus,
  uploadedPdf,
  onFileChange,
  onUpload,
  onDelete,
  tools,

  // Chat related
  question,
  onQuestionChange,
  history,
  onSend,
  isLoading,
  rating,
  selectedModel,
  onModelChange,

  // Device related
  userDevices,
  selectedDevice,
  onDeviceSelect,
  onManageDevices,

  // Analysis related
  showAnalysis,
  repairAnalysis,
  onPerformAnalysis,

  // User
  userId
}) {
  const { t } = useTranslation();

  return (


    <>
      <div className=" absolute top-4 right-4 z-50">
        <LanguageSwitcher />
      </div>
      <div className="flex-1 flex flex-col items-center overflow-y-auto">
        <div className="w-full max-w-4xl px-4 md:px-6 py-6">
          {/* Header */}
          <h1 className="bg-gradient-to-r from-black via-blue-500 to-violet-800 inline-block text-transparent bg-clip-text font-bold text-5xl leading-tight">
            {t('app.title')},
          </h1>
          <br />
          <h1 className="bg-gradient-to-r from-black via-blue-500 to-violet-800 inline-block text-transparent bg-clip-text font-bold text-5xl leading-tight mb-4">
            {t('app.subtitle')}
          </h1>

          {/* Quick Action Buttons */}
          <div className="mb-6">
            <h3 className="text-sm font-medium text-gray-700 mb-3">{t('quickActions.title')}</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
              <button
                onClick={(e) => onSend(e, t('quickActions.toolsQuestion'))}
                className="bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg p-3 text-blue-700 transition-colors duration-200 flex items-center gap-2"
              >
                <span>🛠️</span>
                <span>{t('quickActions.requiredTools')}</span>
              </button>
              <button
                onClick={(e) => onSend(e, t('quickActions.timeQuestion'))}
                className="bg-green-50 hover:bg-green-100 border border-green-200 rounded-lg p-3 text-green-700 transition-colors duration-200 flex items-center gap-2"
              >
                <span>⏱️</span>
                <span>{t('quickActions.timeEstimate')}</span>
              </button>
              <button
                onClick={(e) => onSend(e, t('quickActions.costQuestion'))}
                className="bg-purple-50 hover:bg-purple-100 border border-purple-200 rounded-lg p-3 text-purple-700 transition-colors duration-200 flex items-center gap-2"
              >
                <span>💰</span>
                <span>{t('quickActions.costComparison')}</span>
              </button>
              <button
                onClick={(e) => onSend(e, t('quickActions.difficultyQuestion'))}
                className="bg-orange-50 hover:bg-orange-100 border border-orange-200 rounded-lg p-3 text-orange-700 transition-colors duration-200 flex items-center gap-2"
              >
                <span>📊</span>
                <span>{t('quickActions.difficultyCheck')}</span>
              </button>
            </div>

            {/* Contextual suggestions based on PDF upload */}
            {!uploadedPdf && (
              <div className="mt-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
                <p className="text-sm text-gray-600 text-center">
                  {t('tips.general')}
                </p>
              </div>
            )}

            {uploadedPdf && (
              <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-sm text-blue-700 text-center">
                  {t('tips.pdfMode', { title: uploadedPdf.title })}
                </p>
              </div>
            )}
          </div>

          {/* PDF Upload Interface */}
          <DocumentUpload
            file={file}
            uploadStatus={uploadStatus}
            uploadedPdf={uploadedPdf}
            onFileChange={onFileChange}
            onUpload={onUpload}
            onDelete={onDelete}
          />

          {/* Tool Analysis */}
          <ToolAnalysis
            tools={tools}
            userId={userId}
          />

          {/* Device Selector */}
          <DeviceSelector
            userDevices={userDevices}
            selectedDevice={selectedDevice}
            onDeviceSelect={onDeviceSelect}
            onManageDevices={onManageDevices}
          />

          {/* LLM Model Selector */}
          <div className="mb-4">
            <LLMModelSelector
              selectedModel={selectedModel}
              onModelChange={onModelChange}
              disabled={isLoading}
            />
          </div>

          {/* Chat Interface */}
          <ChatInterface
            question={question}
            onQuestionChange={onQuestionChange}
            history={history}
            onSend={onSend}
            isLoading={isLoading}
            rating={rating}
          />

          {/* Repair Analysis */}
          <RepairAnalysis
            uploadedPdf={uploadedPdf}
            selectedDevice={selectedDevice}
            userId={userId}
            showAnalysis={showAnalysis}
            repairAnalysis={repairAnalysis}
            onPerformAnalysis={onPerformAnalysis}
            chatHistory={history}
            selectedModel={selectedModel}
          />
        </div>
      </div>
    </>



  );
}

export default MainContent;
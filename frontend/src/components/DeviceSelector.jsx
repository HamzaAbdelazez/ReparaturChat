import React from "react";
import { useTranslation } from "react-i18next";

function DeviceSelector({ 
  userDevices, 
  selectedDevice, 
  onDeviceSelect, 
  onManageDevices, 
  onCheckWarranty 
}) {
  const { t } = useTranslation();
  
  const checkWarranty = async (userDeviceId) => {
    try {
      const response = await fetch(`http://localhost:8000/devices/warranty-check/${userDeviceId}`);
      if (response.ok) {
        const warranty = await response.json();
        alert(`${t('devices.warrantyStatus')}: ${warranty.warranty_status}\n${
          warranty.is_under_warranty 
            ? `${t('devices.validUntil')}: ${new Date(warranty.warranty_expires_at).toLocaleDateString()}\n${t('devices.daysRemaining')}: ${warranty.days_remaining}`
            : t('devices.warrantyExpired')
        }`);
      }
    } catch (error) {
      console.error("Error checking warranty:", error);
      alert(t('errors.checkWarrantyFailed'));
    }
  };

  return (
    <div className="bg-white p-4 rounded-xl shadow-md mb-6">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-lg font-semibold">{t('devices.myDevices')}</h3>
        <button
          onClick={onManageDevices}
          className="bg-green-500 hover:bg-green-700 text-white text-sm px-3 py-1 rounded"
        >
          {t('devices.manage')}
        </button>
      </div>
      
      {userDevices.length === 0 ? (
        <p className="text-gray-500 italic">{t('devices.noDevices')}</p>

      ) : (
        <div className="space-y-2">
          {userDevices.map((userDevice) => (
            <div 
              key={userDevice.id} 
              className={`p-3 border rounded cursor-pointer ${
                selectedDevice?.id === userDevice.id ? "border-blue-500 bg-blue-50" : "border-gray-300"
              }`}
              onClick={() => onDeviceSelect(userDevice)}
            >
              <div className="flex justify-between items-center">
                <div>
                  <p className="font-medium">{userDevice.device?.manufacturer} {userDevice.device?.model}</p>
                  <p className="text-sm text-gray-600">{userDevice.device?.category}</p>
                </div>
                <div className="text-right">
                  <span className={`text-xs px-2 py-1 rounded ${
                    userDevice.warranty_status === "active" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                  }`}>
                    {userDevice.warranty_status}
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      checkWarranty(userDevice.id);
                    }}
                    className="ml-2 text-xs bg-blue-500 text-white px-2 py-1 rounded"
                  >
                    Check Warranty
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default DeviceSelector;
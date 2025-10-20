import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Plus, X } from "lucide-react";

function DeviceManager({ userId, onDeviceAdded, onClose }) {
  const { t } = useTranslation();
  const [devices, setDevices] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [newDevice, setNewDevice] = useState({
    manufacturer: "",
    model: "",
    category: "",
    purchaseDate: "",
  });
  const [showAddDevice, setShowAddDevice] = useState(false);
  const [loading, setLoading] = useState(false);

  // Load existing devices
  useEffect(() => {
    loadDevices();
  }, [userId]);

  const loadDevices = async () => {
    try {
      const response = await fetch(`http://localhost:8000/devices/user-devices/${userId}`);
      if (response.ok) {
        const data = await response.json();
        setDevices(data);
      }
    } catch (error) {
      console.error("Error loading devices:", error);
    }
  };

  // Search for device models
  const searchDevices = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:8000/devices/search?manufacturer=${encodeURIComponent(searchQuery)}&model=${encodeURIComponent(searchQuery)}`
      );
      if (response.ok) {
        const data = await response.json();
        setSearchResults(data);
      }
    } catch (error) {
      console.error("Error searching devices:", error);
    }
  };

  // Add device from search results
  const addExistingDevice = async (device) => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/devices/user-devices/?user_id=${userId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          device_id: device.id,
          purchase_date: newDevice.purchaseDate || null,
          warranty_status: "unknown"
        }),
      });

      if (response.ok) {
        await loadDevices();
        onDeviceAdded && onDeviceAdded();
        setSearchQuery("");
        setSearchResults([]);
        setNewDevice({ ...newDevice, purchaseDate: "" });
      }
    } catch (error) {
      console.error("Error adding device:", error);
      alert(t('errors.addDeviceFailed'));
    } finally {
      setLoading(false);
    }
  };

  // Create new device model
  const createNewDevice = async () => {
    if (!newDevice.manufacturer || !newDevice.model || !newDevice.category) {
      alert(t('errors.fillAllFields'));
      return;
    }

    try {
      setLoading(true);
      
      // First create the device model
      const deviceResponse = await fetch("http://localhost:8000/devices/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          manufacturer: newDevice.manufacturer,
          model: newDevice.model,
          category: newDevice.category,
          warranty_period_months: 24,
          repair_complexity: 3
        }),
      });

      if (deviceResponse.ok) {
        const device = await deviceResponse.json();
        
        // Then add it to user's devices
        const userDeviceResponse = await fetch(`http://localhost:8000/devices/user-devices/?user_id=${userId}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            device_id: device.id,
            purchase_date: newDevice.purchaseDate || null,
            warranty_status: "unknown"
          }),
        });

        if (userDeviceResponse.ok) {
          await loadDevices();
          onDeviceAdded && onDeviceAdded();
          setNewDevice({ manufacturer: "", model: "", category: "", purchaseDate: "" });
          setShowAddDevice(false);
        }
      }
    } catch (error) {
      console.error("Error creating device:", error);
      alert(t('errors.createDeviceFailed'));
    } finally {
      setLoading(false);
    }
  };

  const categories = [
    "Washing Machine",
    "Refrigerator", 
    "Dishwasher",
    "Oven",
    "Microwave",
    "Vacuum Cleaner",
    "Air Conditioner",
    "Smartphone",
    "Laptop",
    "TV",
    "Other"
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto mx-4">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">{t('devices.manage')}</h2>
            <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
              <X size={24} />
            </button>
          </div>

          {/* Search Section */}
          <div className="mb-6">
            <h3 className="text-lg font-medium mb-2">{t('devices.addExisting')}</h3>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                placeholder={t('devices.searchPlaceholder')}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 px-3 py-2 border rounded focus:outline-none focus:border-blue-500"
              />
              <button
                onClick={searchDevices}
                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
              >
                {t('devices.search')}
              </button>
            </div>

            {/* Purchase Date for existing devices */}
            <input
              type="date"
              placeholder={t('devices.purchaseDateOptional')}
              value={newDevice.purchaseDate}
              onChange={(e) => setNewDevice({ ...newDevice, purchaseDate: e.target.value })}
              className="w-full px-3 py-2 border rounded focus:outline-none focus:border-blue-500 mb-2"
            />

            {/* Search Results */}
            {searchResults.length > 0 && (
              <div className="border rounded max-h-40 overflow-y-auto">
                {searchResults.map((device) => (
                  <div
                    key={device.id}
                    className="p-3 border-b hover:bg-gray-50 cursor-pointer flex justify-between items-center"
                    onClick={() => addExistingDevice(device)}
                  >
                    <div>
                      <p className="font-medium">{device.manufacturer} {device.model}</p>
                      <p className="text-sm text-gray-600">{device.category}</p>
                    </div>
                    <Plus size={16} className="text-blue-500" />
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Add New Device Section */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <h3 className="text-lg font-medium">{t('devices.addNewDevice')}</h3>
              <button
                onClick={() => setShowAddDevice(!showAddDevice)}
                className="text-blue-500 hover:text-blue-700 text-sm"
              >
                {showAddDevice ? t('devices.cancel') : t('devices.createNew')}
              </button>
            </div>

            {showAddDevice && (
              <div className="border rounded p-4 space-y-3">
                <input
                  type="text"
                  placeholder={t('devices.manufacturerPlaceholder')}
                  value={newDevice.manufacturer}
                  onChange={(e) => setNewDevice({ ...newDevice, manufacturer: e.target.value })}
                  className="w-full px-3 py-2 border rounded focus:outline-none focus:border-blue-500"
                />
                <input
                  type="text"
                  placeholder={t('devices.modelPlaceholder')}
                  value={newDevice.model}
                  onChange={(e) => setNewDevice({ ...newDevice, model: e.target.value })}
                  className="w-full px-3 py-2 border rounded focus:outline-none focus:border-blue-500"
                />
                <select
                  value={newDevice.category}
                  onChange={(e) => setNewDevice({ ...newDevice, category: e.target.value })}
                  className="w-full px-3 py-2 border rounded focus:outline-none focus:border-blue-500"
                >
                  <option value="">{t('devices.selectCategory')}</option>
                  {categories.map((cat) => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
                <input
                  type="date"
                  placeholder={t('devices.purchaseDateOptional')}
                  value={newDevice.purchaseDate}
                  onChange={(e) => setNewDevice({ ...newDevice, purchaseDate: e.target.value })}
                  className="w-full px-3 py-2 border rounded focus:outline-none focus:border-blue-500"
                />
                <button
                  onClick={createNewDevice}
                  disabled={loading}
                  className="w-full bg-green-500 text-white py-2 rounded hover:bg-green-600 disabled:opacity-50"
                >
                  {loading ? t('devices.creating') : t('devices.createAndAdd')}
                </button>
              </div>
            )}
          </div>

          {/* Current Devices */}
          <div>
            <h3 className="text-lg font-medium mb-2">{t('devices.myDevices')} ({devices.length})</h3>
            {devices.length === 0 ? (
              <p className="text-gray-500 italic">{t('devices.noDevicesYet')}</p>
            ) : (
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {devices.map((userDevice) => (
                  <div key={userDevice.id} className="p-3 border rounded">
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="font-medium">
                          {userDevice.device?.manufacturer} {userDevice.device?.model}
                        </p>
                        <p className="text-sm text-gray-600">{userDevice.device?.category}</p>
                        {userDevice.purchase_date && (
                          <p className="text-xs text-gray-500">
                            {t('devices.purchased')}: {new Date(userDevice.purchase_date).toLocaleDateString()}
                          </p>
                        )}
                      </div>
                      <span className={`text-xs px-2 py-1 rounded ${
                        userDevice.warranty_status === "active" 
                          ? "bg-green-100 text-green-800" 
                          : "bg-red-100 text-red-800"
                      }`}>
                        {userDevice.warranty_status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default DeviceManager;
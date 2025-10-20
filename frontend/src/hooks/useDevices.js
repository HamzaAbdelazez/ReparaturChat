import { useState, useCallback } from "react";

export const useDevices = () => {
  const [userDevices, setUserDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [showDeviceManager, setShowDeviceManager] = useState(false);

  // Load user devices
  const loadUserDevices = useCallback(async (userId) => {
    if (!userId) return;
    try {
      const response = await fetch(`http://localhost:8000/devices/user-devices/${userId}`);
      if (response.ok) {
        const devices = await response.json();
        setUserDevices(devices);
      }
    } catch (error) {
      console.error("Error loading user devices:", error);
    }
  }, []);

  return {
    userDevices,
    selectedDevice,
    showDeviceManager,
    setSelectedDevice,
    setShowDeviceManager,
    loadUserDevices
  };
};
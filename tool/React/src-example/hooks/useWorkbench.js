// 工具台 Hook
import { useState, useCallback, useRef, useEffect } from 'react';
import {
  importGeometry,
  generateMesh,
  runSolver,
  connectProgressWS,
} from '../services/workbenchService';

export const useWorkbench = () => {
  const [logs, setLogs] = useState([]);
  const [progress, setProgress] = useState(0);
  const [meshData, setMeshData] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const wsRef = useRef(null);

  // 清理WebSocket
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  /**
   * 添加日志
   */
  const addLog = useCallback((message, level = 'INFO') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { message, level, timestamp }]);
  }, []);

  /**
   * 导入几何文件
   * @param {File} file - 几何文件
   */
  const importGeo = useCallback(async (file) => {
    try {
      addLog(`Importing geometry file: ${file.name}...`);
      const result = await importGeometry(file);
      addLog('Geometry imported successfully', 'SUCCESS');
      return result;
    } catch (error) {
      addLog(`Import failed: ${error.message}`, 'ERROR');
      throw error;
    }
  }, [addLog]);

  /**
   * 生成网格
   * @param {Object} params - 网格参数
   */
  const mesh = useCallback(async (params) => {
    try {
      addLog('Starting mesh generation...');
      setIsRunning(true);
      
      // 连接WebSocket获取进度
      wsRef.current = connectProgressWS(
        (value) => setProgress(value),
        (message) => addLog(message)
      );

      const result = await generateMesh(params);
      setMeshData(result.mesh);
      addLog('Mesh generation completed', 'SUCCESS');
      return result;
    } catch (error) {
      addLog(`Mesh generation failed: ${error.message}`, 'ERROR');
      throw error;
    } finally {
      setIsRunning(false);
      if (wsRef.current) {
        wsRef.current.close();
      }
    }
  }, [addLog]);

  /**
   * 运行求解
   * @param {Object} config - 求解配置
   */
  const solve = useCallback(async (config) => {
    try {
      addLog('Starting solver...');
      setIsRunning(true);
      setProgress(0);

      const result = await runSolver(config);
      addLog('Solver completed successfully', 'SUCCESS');
      return result;
    } catch (error) {
      addLog(`Solver failed: ${error.message}`, 'ERROR');
      throw error;
    } finally {
      setIsRunning(false);
    }
  }, [addLog]);

  /**
   * 清空日志
   */
  const clearLogs = useCallback(() => {
    setLogs([]);
  }, []);

  return {
    logs,
    progress,
    meshData,
    isRunning,
    importGeo,
    mesh,
    solve,
    clearLogs,
  };
};

import React, { createContext, useContext, useState, useCallback } from 'react';
import apiClient, { Scenario, GQueryResult, InputUpdate, APIError } from '../services/api';

interface ScenarioContextType {
  scenario: Scenario | null;
  loading: boolean;
  error: string | null;
  results: Record<string, GQueryResult>;
  createScenario: (areaCode: string, endYear: number, title?: string) => Promise<void>;
  loadScenario: (scenarioId: number) => Promise<void>;
  updateInputs: (inputs: InputUpdate) => Promise<void>;
  fetchResults: (gqueryKeys: string[]) => Promise<void>;
  clearScenario: () => void;
}

const ScenarioContext = createContext<ScenarioContextType | undefined>(undefined);

export const useScenario = () => {
  const context = useContext(ScenarioContext);
  if (!context) {
    throw new Error('useScenario must be used within ScenarioProvider');
  }
  return context;
};

interface ScenarioProviderProps {
  children: React.ReactNode;
}

export const ScenarioProvider: React.FC<ScenarioProviderProps> = ({ children }) => {
  const [scenario, setScenario] = useState<Scenario | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<Record<string, GQueryResult>>({});

  const createScenario = useCallback(async (
    areaCode: string,
    endYear: number,
    title?: string
  ) => {
    setLoading(true);
    setError(null);
    try {
      const newScenario = await apiClient.createScenario({
        area_code: areaCode,
        end_year: endYear,
        title: title || `${areaCode} ${endYear} Scenario`,
      });
      setScenario(newScenario);
    } catch (err) {
      const errorMessage =
        err instanceof APIError
          ? err.message
          : err instanceof Error
          ? err.message
          : 'Failed to create scenario';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const loadScenario = useCallback(async (scenarioId: number) => {
    setLoading(true);
    setError(null);
    try {
      const loadedScenario = await apiClient.getScenario(scenarioId);
      setScenario(loadedScenario);
    } catch (err) {
      const errorMessage =
        err instanceof APIError
          ? err.message
          : err instanceof Error
          ? err.message
          : 'Failed to load scenario';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateInputs = useCallback(async (inputs: InputUpdate) => {
    if (!scenario) {
      throw new Error('No active scenario');
    }
    setLoading(true);
    setError(null);
    try {
      const updatedScenario = await apiClient.updateScenario(scenario.id, inputs);
      setScenario(updatedScenario);
    } catch (err) {
      const errorMessage =
        err instanceof APIError
          ? err.message
          : err instanceof Error
          ? err.message
          : 'Failed to update inputs';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [scenario]);

  const fetchResults = useCallback(async (gqueryKeys: string[]) => {
    if (!scenario) {
      throw new Error('No active scenario');
    }
    setLoading(true);
    setError(null);
    try {
      const newResults = await apiClient.getBatchGQueries(scenario.id, gqueryKeys);
      setResults(prev => ({ ...prev, ...newResults }));
    } catch (err) {
      const errorMessage =
        err instanceof APIError
          ? err.message
          : err instanceof Error
          ? err.message
          : 'Failed to fetch results';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [scenario]);

  const clearScenario = useCallback(() => {
    setScenario(null);
    setResults({});
    setError(null);
  }, []);

  return (
    <ScenarioContext.Provider
      value={{
        scenario,
        loading,
        error,
        results,
        createScenario,
        loadScenario,
        updateInputs,
        fetchResults,
        clearScenario,
      }}
    >
      {children}
    </ScenarioContext.Provider>
  );
};

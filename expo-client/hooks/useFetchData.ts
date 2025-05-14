import { useState } from 'react';
import { usePatientStore } from '@/store/usePatientStore';
import { apiGet } from '@/api';

export const useFetchData = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const setMedications = usePatientStore((state) => state.setMedications);
  const setSymptoms = usePatientStore((state) => state.setSymptoms);

  const fetchMedications = async () => {
    setLoading(true);
    try {
      const data = await apiGet('medications');
      setMedications(data);
    } catch (err) {
      setError('Failed to fetch medications');
    } finally {
      setLoading(false);
    }
  };

  const fetchSymptoms = async () => {
    setLoading(true);
    try {
      const data = await apiGet('symptoms');
      setSymptoms(data);
    } catch (err) {
      setError('Failed to fetch symptoms');
    } finally {
      setLoading(false);
    }
  };

  return { fetchMedications, fetchSymptoms, loading, error };
};

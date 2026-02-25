import { useQuery } from '@tanstack/react-query';
import { fetchGearImages } from '../../../lib/tunerApi';

export function useGearImages(category?: string) {
  return useQuery({
    queryKey: ['tuner', 'gear-images', category],
    queryFn: () => fetchGearImages(category),
    staleTime: 1000 * 60 * 30, // 30 minutes - images don't change
  });
}

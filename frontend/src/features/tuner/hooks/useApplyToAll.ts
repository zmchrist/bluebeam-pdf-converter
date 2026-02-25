import { useMutation, useQueryClient } from '@tanstack/react-query';
import { applyToAll } from '../../../lib/tunerApi';

export function useApplyToAll() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: applyToAll,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tuner', 'icons'] });
    },
  });
}

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchIcons, fetchIcon, saveIcon, createIcon, deleteIcon } from '../../../lib/tunerApi';
import type { IconConfig } from '../../../types/tuner';

export function useIconList() {
  return useQuery({
    queryKey: ['tuner', 'icons'],
    queryFn: fetchIcons,
    staleTime: 1000 * 60 * 5,
  });
}

export function useIconConfig(subject: string | null) {
  return useQuery({
    queryKey: ['tuner', 'icon', subject],
    queryFn: () => fetchIcon(subject!),
    enabled: !!subject,
    staleTime: 1000 * 60,
  });
}

export function useSaveIcon() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ subject, config }: { subject: string; config: Partial<IconConfig> }) =>
      saveIcon(subject, config),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tuner', 'icons'] });
      queryClient.invalidateQueries({ queryKey: ['tuner', 'icon', variables.subject] });
    },
  });
}

export function useCreateIcon() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createIcon,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tuner', 'icons'] });
    },
  });
}

export function useDeleteIcon() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteIcon,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tuner', 'icons'] });
    },
  });
}

import { SortModel } from '@openfun/cunningham-react';

export function sortData<T extends object>(
  data: T[],
  sortModel: SortModel,
): T[] {
  const [sort] = sortModel;

  if (!sort?.sort) {
    return data;
  }

  const field: string = Array.isArray(sort.field)
    ? String(sort.field[0])
    : String(sort.field);

  const direction = sort.sort === 'asc' ? 1 : -1;

  return [...data].sort((a, b) => {
    const aRecord = a as Record<string, unknown>;
    const bRecord = b as Record<string, unknown>;
    const aValue = aRecord[field] as string | number | null | undefined;
    const bValue = bRecord[field] as string | number | null | undefined;

    if (typeof aValue === 'number' && typeof bValue === 'number') {
      return direction * (aValue - bValue);
    }

    return (
      direction *
      String(aValue ?? '').localeCompare(String(bValue ?? ''), undefined, {
        sensitivity: 'base',
      })
    );
  });
}

import { APIError, fetchAPI } from '@/api';
import { getTeamAccesses } from '@/features/teams/member-management';

jest.mock('@/api', () => ({
  fetchAPI: jest.fn(),
}));

describe('getTeamAccesses', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should construct the correct URL with only page', async () => {
    const mockResponse = {
      ok: true,
      json: jest.fn().mockResolvedValue({
        count: 0,
        next: null,
        previous: null,
        results: [],
      }),
    };

    (fetchAPI as jest.Mock).mockResolvedValue(mockResponse);

    await getTeamAccesses({
      page: 1,
      teamId: '123',
      ordering: undefined,
      query: undefined,
    });

    expect(fetchAPI).toHaveBeenCalledWith('teams/123/accesses/?page=1');
  });

  it('should construct the correct URL with only query', async () => {
    const mockResponse = {
      ok: true,
      json: jest.fn().mockResolvedValue({
        count: 0,
        next: null,
        previous: null,
        results: [],
      }),
    };

    (fetchAPI as jest.Mock).mockResolvedValue(mockResponse);

    await getTeamAccesses({
      page: 1,
      teamId: '123',
      ordering: undefined,
      query: 'patricia',
    });

    expect(fetchAPI).toHaveBeenCalledWith('teams/123/accesses/?q=patricia');
  });

  it('should construct the correct URL with ordering and query', async () => {
    const mockResponse = {
      ok: true,
      json: jest.fn().mockResolvedValue({
        count: 0,
        next: null,
        previous: null,
        results: [],
      }),
    };

    (fetchAPI as jest.Mock).mockResolvedValue(mockResponse);

    await getTeamAccesses({
      page: 1,
      teamId: '123',
      ordering: 'user__name',
      query: 'patricia',
    });

    expect(fetchAPI).toHaveBeenCalledWith(
      'teams/123/accesses/?q=patricia&ordering=user__name',
    );
  });

  it('should throw an APIError when the response is not ok', async () => {
    const mockResponse = {
      ok: false,
      json: jest.fn().mockResolvedValue({}),
    };

    (fetchAPI as jest.Mock).mockResolvedValue(mockResponse);

    await expect(
      getTeamAccesses({
        page: 1,
        teamId: '123',
        ordering: undefined,
        query: undefined,
      }),
    ).rejects.toThrow(APIError);

    expect(fetchAPI).toHaveBeenCalledWith('teams/123/accesses/?page=1');
  });
});

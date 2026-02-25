import { CunninghamProvider } from '@gouvfr-lasuite/cunningham-react';
import { render, screen } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import { useTranslation } from 'react-i18next';

import { useTeams } from '@/features/teams/team-management';

import { TeamsListView } from '../TeamsListView';

// Mock the hooks
jest.mock('@/features/teams/team-management', () => ({
  useTeams: jest.fn(),
  TeamsOrdering: {
    BY_CREATED_ON_DESC: '-created_at',
  },
}));
jest.mock('next/navigation');
jest.mock('react-i18next');

describe('TeamsListView', () => {
  const mockTeams = [
    {
      id: '1',
      name: 'Team A',
      accesses: [{ id: '1' }, { id: '2' }],
    },
    {
      id: '2',
      name: 'Team B',
      accesses: [{ id: '3' }],
    },
  ];

  const mockRouter = {
    push: jest.fn(),
  };

  const renderWithProvider = (ui: React.ReactElement) => {
    return render(<CunninghamProvider>{ui}</CunninghamProvider>);
  };

  beforeEach(() => {
    // Setup mock implementations
    (useTeams as jest.Mock).mockReturnValue({
      data: mockTeams,
      isLoading: false,
    });
    (useRouter as jest.Mock).mockReturnValue(mockRouter);
    (useTranslation as jest.Mock).mockReturnValue({
      t: (key: string) => key,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders teams list when teams exist', () => {
    renderWithProvider(<TeamsListView querySearch="" />);

    // Check if team names are rendered
    expect(screen.getByText('Team A')).toBeInTheDocument();
    expect(screen.getByText('Team B')).toBeInTheDocument();

    // Check if member counts are rendered
    expect(screen.getByText('2')).toBeInTheDocument(); // Team A has 2 members
    expect(screen.getByText('1')).toBeInTheDocument(); // Team B has 1 member
  });

  it('shows "No teams exist" message when no teams are available', () => {
    (useTeams as jest.Mock).mockReturnValue({
      data: [],
      isLoading: false,
    });

    renderWithProvider(<TeamsListView querySearch="" />);
    expect(screen.getByText('No teams exist.')).toBeInTheDocument();
  });

  it('filters teams based on search query', () => {
    renderWithProvider(<TeamsListView querySearch="Team A" />);

    // Only Team A should be visible
    expect(screen.getByText('Team A')).toBeInTheDocument();
    expect(screen.queryByText('Team B')).not.toBeInTheDocument();
  });

  it('navigates to team details when clicking the view button', () => {
    renderWithProvider(<TeamsListView querySearch="" />);

    // Find and click the view button for Team A
    const viewButtons = screen.getAllByRole('button', {
      name: 'View team details',
    });
    viewButtons[0].click();

    // Check if router.push was called with the correct path
    expect(mockRouter.push).toHaveBeenCalledWith('/teams/1');
  });

  it('handles case-insensitive search', () => {
    renderWithProvider(<TeamsListView querySearch="team a" />);

    // Team A should still be visible despite different case
    expect(screen.getByText('Team A')).toBeInTheDocument();
    expect(screen.queryByText('Team B')).not.toBeInTheDocument();
  });
});

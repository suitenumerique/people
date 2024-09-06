import { ModalSize } from '@openfun/cunningham-react';
import { render, screen, waitFor } from '@testing-library/react';
import React from 'react';

import { AppWrapper } from '@/tests/utils';

import { Modal, usePreventFocusVisible } from '../Modal';

describe('usePreventFocusVisible hook', () => {
  const TestComponent = () => {
    usePreventFocusVisible(['.test-element']);

    return (
      <div>
        <div className="test-element">Test Element</div>
      </div>
    );
  };

  const originalMutationObserver = global.MutationObserver;

  const mockDisconnect = jest.fn();
  const mutationObserverMock = jest.fn(function MutationObserver(
    callback: MutationCallback,
  ) {
    this.observe = () => {
      callback([{ type: 'childList' }] as MutationRecord[], this);
    };

    this.disconnect = mockDisconnect;
  });

  afterEach(() => jest.clearAllMocks());

  beforeAll(
    () =>
      (global.MutationObserver =
        mutationObserverMock as unknown as typeof MutationObserver),
  );

  afterAll(() => (global.MutationObserver = originalMutationObserver));

  test('sets tabindex to -1 on the target elements', () => {
    const { unmount } = render(<TestComponent />);

    const targetElement = screen.getByText('Test Element');

    expect(targetElement).toHaveAttribute('tabindex', '-1');

    unmount();

    expect(mockDisconnect).toHaveBeenCalled();
  });
});

describe('Modal', () => {
  test('applies usePreventFocusVisible and sets tabindex', async () => {
    render(
      <Modal
        isOpen={true}
        onClose={() => {}}
        size={ModalSize.MEDIUM}
        title={<h3>Test Modal Title</h3>}
        leftActions={<button>Cancel</button>}
        rightActions={<button>Submit</button>}
      >
        <p>Modal content</p>
      </Modal>,
      { wrapper: AppWrapper },
    );

    /* eslint-disable testing-library/no-node-access */
    const modalContent = document.querySelector('.c__modal__content');
    /* eslint-enable testing-library/no-node-access */

    await waitFor(() => {
      expect(modalContent).toHaveAttribute('tabindex', '-1');
    });
  });
});

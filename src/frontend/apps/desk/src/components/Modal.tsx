import {
  Modal as CunninghamModal,
  ModalProps,
} from '@openfun/cunningham-react';
import React, { useEffect } from 'react';

// Define a wrapper component that extends ModalProps to accept the same props as the Modal
export const Modal: React.FC<ModalProps> = ({ children, ...props }) => {
  // Apply the hook here once for all modals
  usePreventFocusVisible(['.c__modal__content']);

  return <CunninghamModal {...props}>{children}</CunninghamModal>;
};

/**
 * @description used to prevent elements to be navigable by keyboard when only a DOM mutation causes the elements to be
 * in the document
 * @see https://github.com/suitenumerique/people/pull/379
 */
export const usePreventFocusVisible = (elements: string[]) => {
  useEffect(() => {
    const observer = new MutationObserver((mutationsList) => {
      mutationsList.forEach(() => {
        elements.forEach((selector) =>
          document.querySelector(selector)?.setAttribute('tabindex', '-1'),
        );
        observer.disconnect();
      });
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });

    return () => {
      observer.disconnect();
    };
  }, [elements]);

  return null;
};

import {
  Modal as CunninghamModal,
  ModalProps,
} from '@gouvfr-lasuite/cunningham-react';
import React, { useEffect } from 'react';

import { HorizontalSeparator } from '@/components';

import style from './custom-modal.module.scss';

export const CustomModal: React.FC<
  ModalProps & { step?: number; totalSteps?: number }
> = ({ children, step = 0, totalSteps = 1, ...props }) => {
  // Apply the hook here once for all modals
  usePreventFocusVisible(['.c__modal__content']);

  return (
    <CunninghamModal {...props}>
      {/*<div className={style.modalContainer} onClick={(e) => e.stopPropagation()}>        */}
      {/* modal header */}
      {totalSteps > 1 && (
        <div className={style.header}>
          <div className={style.progressBar}>
            {Array.from({ length: totalSteps }).map((_, index) => (
              <div
                key={index}
                className={`${style.progressBarStep} ${index <= step ? style.active : ''}`}
              ></div>
            ))}
          </div>
        </div>
      )}
      <HorizontalSeparator $withPadding={true}></HorizontalSeparator>
      <div>
        {children}
        {/* modal content */}
        {/*<div className={style.content}>{children}</div>*/}

        {/* modal footer */}
      </div>
      <div className={style.footer}></div>

      {/*</div>*/}
    </CunninghamModal>
  );
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

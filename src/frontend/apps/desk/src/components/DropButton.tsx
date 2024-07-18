import React, {
  PropsWithChildren,
  ReactNode,
  useEffect,
  useRef,
  useState,
} from 'react';
import { Button, DialogTrigger, Popover } from 'react-aria-components';
import styled, { createGlobalStyle } from 'styled-components';

const StyledPopover = styled(Popover)`
  background-color: white;
  border-radius: 4px;
  box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.1);
  padding: 0.5rem;
  border: 1px solid #dddddd;
  opacity: 0;
  transition: opacity 0.2s ease-in-out;
`;

const StyledButton = styled(Button)`
  cursor: pointer;
  border: none;
  background: none;
  outline: none;
  transition: all 0.2s ease-in-out;
  font-family: Marianne, Arial, serif;
  font-weight: 500;
  font-size: 0.938rem;
  text-wrap: nowrap;
`;

const GlobalStyle = createGlobalStyle`
  &:focus-visible {
    outline: none;
  }
`;

interface DropButtonProps {
  button: ReactNode;
  isOpen?: boolean;
  onOpenChange?: (isOpen: boolean) => void;
}

export const DropButton = ({
  button,
  isOpen = false,
  onOpenChange,
  children,
}: PropsWithChildren<DropButtonProps>) => {
  const [opacity, setOpacity] = useState(false);
  const [isLocalOpen, setIsLocalOpen] = useState(isOpen);

  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setIsLocalOpen(isOpen);
  }, [isOpen]);

  useEffect(() => {
    if (ref.current) {
      ref.current[isLocalOpen ? 'focus' : 'blur']();
    }
  }, [isLocalOpen]);

  const onOpenChangeHandler = (isOpen: boolean) => {
    setIsLocalOpen(isOpen);
    onOpenChange?.(isOpen);
    setTimeout(() => {
      setOpacity(isOpen);
    }, 10);
  };

  return (
    <>
      <GlobalStyle />
      <DialogTrigger onOpenChange={onOpenChangeHandler} isOpen={isLocalOpen}>
        <StyledButton>{button}</StyledButton>
        <StyledPopover
          style={{ opacity: opacity ? 1 : 0 }}
          isOpen={isLocalOpen}
          onOpenChange={onOpenChangeHandler}
        >
          <div ref={ref} tabIndex={-1}>
            {children}
          </div>
        </StyledPopover>
      </DialogTrigger>
    </>
  );
};

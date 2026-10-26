import {
  LASUITE_SUPPORT_API_URL,
  LASUITE_SUPPORT_SCRIPT_URL,
} from '@/core/lasuite';

const SUPPORT_CHANNEL = 'accounts';
const SUPPORT_SCRIPT_ID = 'lasuite-support-widget';
const SUPPORT_WIDGET = 'support';
const SUPPORT_HOST_ID = 'lasuite-widget-support-root';
const SUPPORT_CLOSED_EVENT = 'lasuite-widget-support-closed';

declare global {
  interface Window {
    _lasuite_widget?: unknown[];
  }
}

const loadSupportScript = () => {
  if (document.getElementById(SUPPORT_SCRIPT_ID)) {
    return;
  }

  const script = document.createElement('script');
  script.id = SUPPORT_SCRIPT_ID;
  script.src = LASUITE_SUPPORT_SCRIPT_URL;
  script.async = true;
  document.body.appendChild(script);
};

const closeOnOutsidePointerDown = (event: PointerEvent) => {
  if (
    document.getElementById(SUPPORT_HOST_ID)?.contains(event.target as Node)
  ) {
    return;
  }
  window._lasuite_widget?.push([SUPPORT_WIDGET, 'close']);
};

const stopClosingOnOutsidePointerDown = () => {
  document.removeEventListener('pointerdown', closeOnOutsidePointerDown);
};

export const openSupportWidget = (email?: string) => {
  document.addEventListener('pointerdown', closeOnOutsidePointerDown);
  document.addEventListener(
    SUPPORT_CLOSED_EVENT,
    stopClosingOnOutsidePointerDown,
    { once: true },
  );

  window._lasuite_widget = window._lasuite_widget || [];
  window._lasuite_widget.push([
    SUPPORT_WIDGET,
    'init',
    {
      api: LASUITE_SUPPORT_API_URL,
      channel: SUPPORT_CHANNEL,
      position: 'bottom-left',
      email,
    },
  ]);
  loadSupportScript();
};

import { fireEvent } from '@testing-library/react';

import { openSupportWidget } from '../openSupportWidget';

const SUPPORT_CLOSE_COMMAND = ['support', 'close'];

describe('openSupportWidget', () => {
  afterEach(() => {
    document.dispatchEvent(new Event('lasuite-widget-support-closed'));
    document.body.innerHTML = '';
    delete window._lasuite_widget;
  });

  it('closes the form on a click outside it', () => {
    openSupportWidget();

    fireEvent.pointerDown(document.body);

    expect(window._lasuite_widget).toContainEqual(SUPPORT_CLOSE_COMMAND);
  });

  it('keeps the form open on a click inside it', () => {
    const widgetHost = document.createElement('div');
    widgetHost.id = 'lasuite-widget-support-root';
    document.body.appendChild(widgetHost);
    openSupportWidget();

    fireEvent.pointerDown(widgetHost);

    expect(window._lasuite_widget).not.toContainEqual(SUPPORT_CLOSE_COMMAND);
  });

  it('stops listening for outside clicks once the form is closed', () => {
    openSupportWidget();
    document.dispatchEvent(new Event('lasuite-widget-support-closed'));

    fireEvent.pointerDown(document.body);

    expect(window._lasuite_widget).not.toContainEqual(SUPPORT_CLOSE_COMMAND);
  });
});

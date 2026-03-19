import { Button } from '@gouvfr-lasuite/cunningham-react';
import clsx from 'clsx';
import React, { ReactNode, useState } from 'react';

import { Icon } from '@/components';

import style from './custom-tabs.module.scss';

export type TabData = {
  id: string;
  label: string;
  iconName?: string;
  icon?: ReactNode;
  subtext?: string;
  content: ReactNode;
};

export type TabsProps = {
  theme?: 'brand' | 'neutral';
  orientation?: 'horizontal' | 'vertical';
  tabs: TabData[];
  defaultSelectedTab?: string;
  fullWidth?: boolean;
};

export const CustomTabs = ({
  orientation = 'horizontal',
  theme = 'brand',
  tabs,
  defaultSelectedTab,
  fullWidth = false,
}: TabsProps) => {
  const [selectedTabId, setSelectedTabId] = useState(
    defaultSelectedTab ?? tabs[0]?.id,
  );

  const activeTab =
    tabs.find((tab) => tab.id === selectedTabId) ?? tabs[0] ?? null;

  if (tabs.length === 0 || !activeTab) {
    return null;
  }

  return (
    <div
      className={clsx(style.root, {
        [style.fullWidth]: fullWidth,
        [style.neutral]: theme === 'neutral',
        [style.orientationVertical]: orientation === 'vertical',
      })}
    >
      <div
        style={{
          display: 'flex',
        }}
      >
        <div
          style={{
            display: 'inline-flex',
            width: 'auto',
            flexDirection: orientation === 'horizontal' ? 'row' : 'column',
            alignItems: 'center',
            borderRadius: 8,
            backgroundColor:
              'var(--c--contextuals--background--surface--primary)',
            backdropFilter: 'blur(10px)',
            border: '1px solid var(--c--contextuals--border--surface--primary)',
            padding: 4,
            boxShadow: 'rgba(0, 0, 0, 0.05) 0px 2px 4px 0px',
            gap: 4,
          }}
        >
          {tabs.map((tab) => {
            const isSelected = tab.id === activeTab?.id;
            return (
              <Button
                key={tab.id}
                onClick={() => setSelectedTabId(tab.id)}
                variant={isSelected ? 'secondary' : 'tertiary'}
                color={isSelected ? 'brand' : 'neutral'}
                size="small"
                aria-pressed={isSelected}
                icon={
                  <Icon
                    iconName={tab.iconName ?? ''}
                    $color={isSelected ? 'brand' : 'neutral'}
                  />
                }
              >
                {tab.icon && !tab.iconName && tab.icon}
                <span>
                  <span className="react-aria-Tab__title">{tab.label}</span>
                  {tab.subtext && orientation === 'vertical' && (
                    <span className="react-aria-Tab__subtext">
                      {tab.subtext}
                    </span>
                  )}
                </span>
              </Button>
            );
          })}
        </div>
      </div>
      {activeTab && (
        <div style={{ marginTop: 8, width: '100%' }}>{activeTab.content}</div>
      )}
    </div>
  );
};

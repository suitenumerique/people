import * as React from 'react';
import { ReactNode } from 'react';
import { Tab, TabList, TabPanel, Tabs } from 'react-aria-components';

import { Box } from '@/components';

import style from './custom-tabs.module.scss';

type TabsOption = {
  ariaLabel?: string;
  label: string;
  iconName?: string;
  id?: string;
  content: ReactNode;
};

type Props = {
  tabs: TabsOption[];
};

export const CustomTabs = ({ tabs }: Props) => {
  return (
    <div className={style.customTabsContainer}>
      <Tabs>
        <TabList>
          {tabs.map((tab) => {
            const id = tab.id ?? tab.label;
            return (
              <Tab key={id} aria-label={tab.ariaLabel} id={id}>
                <Box $direction="row" $gap="5px">
                  {tab.iconName && (
                    <span className="material-icons" aria-hidden="true">
                      {tab.iconName}
                    </span>
                  )}
                  {tab.label}
                </Box>
              </Tab>
            );
          })}
        </TabList>

        {tabs.map((tab) => {
          const id = tab.id ?? tab.label;
          return (
            <TabPanel key={id} id={id}>
              {tab.content}
            </TabPanel>
          );
        })}
      </Tabs>
    </div>
  );
};

import { Tabs, TabList, Tab, TabPanel } from "react-aria-components";
import { TabData } from "./types";
import clsx from "clsx";
import style from './custom-tabs.module.scss';

export type TabsProps = {
  theme?: "brand" | "neutral";
  orientation?: "horizontal" | "vertical";
  tabs: TabData[];
  defaultSelectedTab?: string;
  fullWidth?: boolean;
};

export const CustomTabs = ({
  orientation = "horizontal",
  theme = 'brand',
  tabs,
  defaultSelectedTab,
  fullWidth = false,
}: TabsProps) => {
  if (tabs.length === 0) {
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
      <Tabs defaultSelectedKey={defaultSelectedTab}>
        <TabList aria-label="menu">
          {tabs.map((tab) => (
            <Tab key={tab.id} id={tab.id}>
              {tab.icon && <span aria-hidden="true" className="material-icons">{tab.icon}</span>}
              <span>
                <span className="react-aria-Tab__title">{tab.label}</span>
               { tab.subtext && orientation === 'vertical' && <span className="react-aria-Tab__subtext">{tab.subtext}</span> }
              </span>
            </Tab>
          ))}
        </TabList>
        {tabs.map((tab) => (
          <TabPanel key={tab.id} id={tab.id}>
            {tab.content}
          </TabPanel>
        ))}
      </Tabs>
    </div>
  );
};

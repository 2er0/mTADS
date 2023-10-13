// hooks/useData.ts
import { useEffect, useState } from "react";
import * as YAML from "js-yaml";

export const useData = () => {
  const [options, setOptions] = useState<string[]>([]);

  interface YamlDataItem {
    a_t: number[];
    anomalies: { kinds: { kind: string }[] }[];
    channels: number;
    feature_columns: string[];
    name: string;
    [key: string]: any;
  }

  const fetchNames = () => {
    const urls = [
      "https://raw.githubusercontent.com/2er0/mTADS/main/srb_timeseries/overview.yaml",
    ];

    Promise.all(
      urls.map((url) =>
        fetch(url)
          .then((response) => {
            if (!response.ok) {
              throw new Error(
                "Network response was not ok: " + response.statusText
              );
            }
            return response.text();
          })
          .then((data) => {
              const jsonData = YAML.load(data) as {
                "srb-timeseries": YamlDataItem[];
              };
              return jsonData && jsonData["srb-timeseries"]
                ? jsonData["srb-timeseries"].map(
                    (item: YamlDataItem) => item.name
                  )
                : [];
          })
      )
    )
      .then((namesArrays) => {
        const allNames = namesArrays.flatMap((names) => names);
        setOptions(allNames);
      })
      .catch((error) => {
        console.error(
          "There has been a problem with your fetch operation:",
          error
        );
      });
  };

  useEffect(() => {
    fetchNames();
    // TODO: Implement fetching and processing for `processedData` similar to `fetchNames`
  }, []);

  return options || [];
};

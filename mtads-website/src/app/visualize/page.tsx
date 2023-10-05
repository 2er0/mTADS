"use client";
import React, { useEffect, useRef, useState } from "react";
import Link from "next/link";
import Dropdown from "../../components/dropdownMenu";
import { useSearchParams } from "next/navigation";
import * as d3 from "d3";
import * as YAML from "js-yaml";

const Page = () => {
  const d3Container = useRef(null);
  //const options = ["Train", "Test", "Validation"];
  const [options, setOptions] = useState<string[]>([]);

  const fetchSearch = async (url: string) => {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(response.statusText);
    }
    const res = JSON.stringify(response);
    return response.json();
  };

  const search = useSearchParams();
  const searchQuery = search ? search.get("q") : null;
  const encodedValue = encodeURIComponent(searchQuery || "");

  interface YamlDataItem {
    a_t: number[];
    anomalies: { kinds: { kind: string }[] }[];
    channels: number;
    feature_columns: string[];
    name: string;
    [key: string]: any;
  }

  const fetchNames = () => {
    fetch("fsb_timeseries/overview.yaml")
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
          "fsb-timeseries": YamlDataItem[];
        };
        const names = jsonData["fsb-timeseries"].map(
          (item: YamlDataItem) => item.name
        );
        setOptions(names);
      })
      .catch((error) => {
        console.error(
          "There has been a problem with your fetch operation:",
          error
        );
      });
  };

  interface DataPoint {
    timestamp: number;
    [key: string]: number;
  }

  interface RawDataPoint {
    timestamp: string;
    [key: string]: string;
  }

  useEffect(() => {
    fetchNames();
    if (d3Container.current) {
      d3.select(d3Container.current).selectAll("*").remove();
      // Set the dimensions and margins of the graph
      let margin = { top: 20, right: 20, bottom: 30, left: 50 },
        width = 960 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

      // Set the ranges
      let x = d3.scaleLinear().range([0, width]);
      let y = d3.scaleLinear().range([height, 0]);

      // Define the line
      let valueline = d3
        .line<DataPoint>()
        .x((d) => x(d.timestamp))
        .y((d) => y(d["value-0"]));

      let valueline2 = d3
        .line<DataPoint>()
        .x((d) => x(d.timestamp))
        .y((d) => y(d["value-1"]));

      let svg = d3
        .select(d3Container.current)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

        const filePath = `fsb_timeseries/${encodedValue}/train_anomaly.csv`;

      d3.csv(filePath).then((data: d3.DSVRowArray<string>) => {
        // Explicitly define the structure expected in the CSV for safety
        const processedData: DataPoint[] = data.map((d: any) => {
          return {
            timestamp: +d.timestamp,
            ...d,
          };
        });

        const keys = Object.keys(data[0]).filter((k) => k !== "timestamp");

        x.domain(d3.extent(data, (d) => +d.timestamp) as [number, number]);

        y.domain([
          0,
          d3.max(data, (d) => Math.max(...keys.map((key) => +d[key]))) ?? 0,
        ]);

        const lines = keys.map((key, i) => {
          return d3
            .line<DataPoint>()
            .x((d) => x(d.timestamp))
            .y((d) => y(d[key as keyof DataPoint]));
        });

        // Add the lines path.
        lines.forEach((line, i) => {
          svg
            .append("path")
            .data([processedData])
            .attr("class", "line")
            .attr("d", line)
            .style("stroke", d3.schemeCategory10[i]); // Different color for each line
        });

        // Add the X Axis
        svg
          .append("g")
          .attr("transform", `translate(0, ${height})`)
          .call(d3.axisBottom(x));

        // Add the Y Axis
        svg.append("g").call(d3.axisLeft(y));
      });
    }
  }, [d3Container.current, encodedValue]);

  return (
    <div>
      <div className="flex flex-col min-h-screen">
        <Dropdown options={options} />
        <div
          className="flex justify-center items-center h-screen"
          ref={d3Container}
        />{" "}
        {/* This div is where we will append our graph */}
      </div>

      <div>
        <footer className="flex items-center justify-center w-full h-24 border-t">
          <p className="mr-1">Laget av</p>
          <Link href="https://github.com/villi02">
            <p className="hover:text-pink-400">Vilhjalmur Arnar Vilhjalmsson</p>
          </Link>
        </footer>
      </div>
    </div>
  );
};

export default Page;

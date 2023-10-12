"use client";
import React, { useEffect, useRef, useState } from "react";
import Link from "next/link";
import Dropdown from "../../components/dropdownMenu";
import { useSearchParams } from "next/navigation";
import * as d3 from "d3";
import { useData } from "@/hooks/useData";

const Page = () => {
  const d3Container = useRef(null);

  const search = useSearchParams();
  const searchQuery = search ? search.get("q") : null;
  const encodedValue = encodeURIComponent(searchQuery || "");

  interface DataPoint {
    timestamp: number;
    [key: string]: number;
  }
  const options = useData();

  useEffect(() => {
    if (d3Container.current) {
      d3.select(d3Container.current).selectAll("*").remove();
      // Set the dimensions and margins of the graph
      const fileNames = [
        "train_anomaly.csv",
        "train_no_anomaly.csv",
        "test.csv",
      ];
      fileNames.forEach((fileName, i) => {
        const filePath = `fsb_timeseries/${encodedValue}/${fileName}`;

        let margin = { top: 20, right: 20, bottom: 30, left: 50 },
          width = 960 - margin.left - margin.right,
          height = 500 - margin.top - margin.bottom;

        // Set the ranges
        let x = d3.scaleLinear().range([0, width]);
        let y = d3.scaleLinear().range([height, 0]);

        let svg = d3
          .select(d3Container.current)
          .append("svg")
          .attr("width", width + margin.left + margin.right)
          .attr("height", height + margin.top + margin.bottom + 50) // Add space below each plot
          .append("g")
          .attr("transform", `translate(${margin.left}, ${margin.top})`);

        d3.csv(filePath)
          .then((data: d3.DSVRowArray<string>) => {
            // Explicitly define the structure expected in the CSV for safety
            const processedData: DataPoint[] = data.map(
              (d: d3.DSVRowString<string>) => {
                return {
                  timestamp: +d.timestamp,
                  ...d,
                } as DataPoint;
              }
            );

            const keys = Object.keys(data[0]).filter((k) => k !== "timestamp");

            x.domain([0, data.length - 1]);

            const allYValues = data.reduce((accum: number[], curr) => {
              keys.forEach((key) => accum.push(+curr[key]));
              return accum;
            }, []);

            const minY = Math.min(...allYValues);
            const maxY = Math.max(...allYValues);

            // Dynamically adjust height if necessary.
            // For example, if there is a negative minY value, provide more space. Adjust as per your visualization needs.
            if (minY < 0) {
              height = height - minY;
            }

            y.domain([minY, maxY]);

            svg
              .append("text")
              .attr("x", width / 2)
              .attr("y", 0 - margin.top / 2)
              .attr("text-anchor", "middle")
              .style("font-size", "16px")
              .style("text-decoration", "underline")
              .style("fill", "white")
              .text(fileName);

            // Add the X Axis
            svg
              .append("g")
              .attr("transform", `translate(0, ${height})`)
              .call(d3.axisBottom(x))
              .attr("class", "axis x-axis")
              .selectAll("text")
              .style("fill", "white");

            // Add the Y Axis
            svg
              .append("g")
              .call(d3.axisLeft(y))
              .attr("class", "axis y-axis")
              .selectAll("text")
              .style("fill", "white");

            const lines = keys.map((key, i) => {
              return d3
                .line<DataPoint>()
                .x((d, i) => x(i)) // Use the index i instead of d.timestamp
                .y((d) => y(d[key as keyof DataPoint]));
            });

            // Add the lines path.
            lines.forEach((line, i) => {
              const pathData = line(processedData);
              svg
                .append("path")
                .data([processedData])
                .attr("class", "line")
                .attr("d", pathData)
                .style("stroke", d3.schemeCategory10[i - 1])
                .style("fill", "none");
            });
          })
          .catch((error) => {
            console.error("Error loading data:", error);
          });
      });
    }
  }, [d3Container.current, encodedValue]);

  return (
    <div>
      <div className="flex flex-col min-h-screen">
        <Dropdown options={options} />
        <div
          className="flex flex-col items-center w-full"
          ref={d3Container}
        />{" "}
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

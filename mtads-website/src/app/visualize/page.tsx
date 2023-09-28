"use client";
import React, { useEffect, useRef } from "react";
import Link from "next/link";
import Dropdown from "../../components/dropdownMenu";
import * as d3 from "d3";

const Page = () => {
  const d3Container = useRef(null);
  const options = ["Train", "Test", "Validation"];

  interface DataPoint {
    timestamp: number;
    "value-0": number;
    "value-1": number;
  }

  interface RawDataPoint {
    timestamp: string;
    "value-0": number;
    "value-1": number;
  }

  useEffect(
    () => {
      if (d3Container.current) {
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
          .attr(
            "transform",
            "translate(" + margin.left + "," + margin.top + ")"
          );

        // Get the data
        d3.csv<any>("train_anomaly.csv").then((data) => {
          const processedData = data.map((d: any) => ({
            timestamp: +d.timestamp, // convert string to number using unary plus operator
            "value-0": +d["value-0"],
            "value-1": +d["value-1"],
          }));

          // Scale the range of the data
          x.domain(
            d3.extent(data, function (d) {
              return +d.timestamp;
            }) as [number, number] // The as assertion ensures TypeScript that the result is a tuple of numbers
          );
          y.domain([
            0,
            d3.max(data, function (d) {
              return Math.max(+d["value-0"], +d["value-1"]);
            }) ?? 0, // The nullish coalescing operator (??) returns its right-hand side operand when its left-hand side operand is null or undefined.
          ]);

          // Add the valueline path.
          svg
            .append("path")
            .data([data])
            .attr("class", "line")
            .attr("d", valueline as any)
            .style("stroke", "#ff0000");

          // Add the valueline2 path.
          svg
            .append("path")
            .data([data])
            .attr("class", "line")
            .attr("d", valueline2 as any)
            .style("stroke", "#00ff00"); 

          // Add the X Axis
          svg
            .append("g")
            .attr("transform", "translate(0," + height + ")")
            .call(d3.axisBottom(x));

          // Add the Y Axis
          svg.append("g").call(d3.axisLeft(y));
        });
      }
    },

    [] // run effect only once
  );

  return (
    <div>
      <div className="flex flex-col min-h-screen">
        <Dropdown options={options} />
        <div className="flex justify-center items-center h-screen" ref={d3Container} />{" "}
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

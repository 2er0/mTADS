"use client";
import React, {useEffect, useRef, useState} from "react";
import Link from "next/link";
import Dropdown from "../../components/dropdownMenu";
import {useSearchParams} from "next/navigation";
import * as d3 from "d3";
import {useData} from "@/hooks/srbUseData";

const Page = () => {

    const search = useSearchParams();
    const searchQuery = search ? search.get("q") : null;
    const encodedValue = encodeURIComponent(searchQuery || "");

    const options = useData();
    const baseUrl = "srb-visualize";

    const github_base_url = `https://raw.githubusercontent.com/2er0/mTADS/main/srb_timeseries/${encodedValue}`;

    const fileNames = []
    if (encodedValue == "") {
        fileNames.push(
            "./nodata.png",
            "./nodata.png",
            "./nodata.png"
        );
    } else {
        fileNames.push(
            `${github_base_url}/train_anomaly.png`,
            `${github_base_url}/train_no_anomaly.png`,
            `${github_base_url}/test.png`
        );
    }

    let margin = {top: 20, right: 20, bottom: 30, left: 50},
        magic_height = 150,
        width = 960 - margin.left - margin.right,
        height = document.body.scrollHeight / 3 - magic_height - margin.top - margin.bottom;

    return (
        <div>
            <div className="flex">
                <h1 className="text-5xl font-bold p-4">
                    <a href="/mTADS/">
                        &larr; mTADS
                    </a>
                     &nbsp;| Semi-realistic benchmark suite
                </h1>
            </div>
            <div className="flex flex-col min-h-screen">
                <Dropdown options={options} baseUrl={baseUrl}/>
                <div className="flex flex-col items-center w-full">
                    <div className="p-4">
                        <p>train_anomaly.png</p>
                        <img src={fileNames[0]} style={{height:height}}/>
                    </div>
                    <p className="p-4">
                        <p>train_no_anomaly.png</p>
                        <img src={fileNames[1]} style={{height:height}}/>
                    </p>
                    <p className="p-4">
                        <p>test.png</p>
                        <img src={fileNames[2]} style={{height:height}}/>
                    </p>
                </div>
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

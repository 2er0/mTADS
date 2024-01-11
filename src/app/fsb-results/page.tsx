"use client";
import React, {useEffect, useRef, useState} from "react";
import Papa from "papaparse";
import Dropdown from "../../components/dropdownMenu";
import {DataTable} from "./DataTable";
import {columns, DatasetResults} from "./Column";
import Link from "next/link";
import {useData} from "@/hooks/useData";
import {useSearchParams} from "next/navigation";

const Page = () => {

    const baseUrl = "fsb-results";
    const options = useData();
    const [data, setData] = useState<DatasetResults[]>([]);

    const search = useSearchParams();
    const searchQuery = search ? search.get("q") : null;
    const encodedValue = encodeURIComponent(searchQuery || "");

    useEffect(() => {
        console.log(data)
        if (encodedValue == "") {
            return;
        }

        // setData([
        //     {
        //         index: 0,
        //         dataset: "uiae",
        //         rtype: "1",
        //         Test_AVERAGE_PRECISION: 0.5,
        //         Test_F1Score_PercentileThresholding: 0.5,
        //         Test_FIXED_RANGE_PR_AUC: 0.5,
        //         Test_PR_AUC: 0.5,
        //         Test_RANGE_PR_AUC: 0.5,
        //         Test_ROC_AUC: 0.5,
        //         Test_THRESHOLD: 0.5,
        //         Train_AVERAGE_PRECISION: 0.5,
        //         Train_F1Score_PercentileThresholding: 0.5,
        //         Train_FIXED_RANGE_PR_AUC: 0.5,
        //         Train_PR_AUC: 0.5,
        //         Train_RANGE_PR_AUC: 0.5,
        //         Train_ROC_AUC: 0.5
        //     }
        // ]);
        Papa.parse(`/Users/davidb/PycharmProjects/timeflow/base_line/result_aggregation/results/by-dataset/${encodedValue}.csv`,
            {
                download: true,
                header: true,
                complete: (results) => {
                    console.log("CSV", results);
                    setData(results);
                }
            });

    }, [encodedValue]);

    return (
        <div>
            <div className="flex">
                <h1 className="text-5xl font-bold p-4">
                    <a href="/mTADS/">
                        &larr; mTADS
                    </a>
                    &nbsp;| Fully synthetic benchmark suite
                </h1>
            </div>
            <div className="flex flex-col min-h-screen">
                <Dropdown options={options} baseUrl={baseUrl}/>
                {/*<DataTable columns={columns} data={data}/>*/}
                {" "}
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

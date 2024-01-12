"use client";
import React, {useEffect, useRef, useState} from "react";
import Papa from "papaparse";
import Dropdown from "../../components/dropdownMenu";
import Link from "next/link";
import {useData} from "@/hooks/srbUseData";
import {useSearchParams} from "next/navigation";
import SimpleDataTable from "@/components/SimpleDataTable";




const Page = () => {

    const baseUrl = "srb-results";
    const options = useData();

    const search = useSearchParams();
    const searchQuery = search ? search.get("q") : null;
    const encodedValue = encodeURIComponent(searchQuery || "");

    const columns = ["dataset", "rtype", "Test_ROC_AUC", "Test_RANGE_PR_AUC",
        "Test_F1Score_PercentileThresholding", "Test_AVERAGE_PRECISION", "Test_PR_AUC", "Test_FIXED_RANGE_PR_AUC",
        "Train_ROC_AUC", "Train_RANGE_PR_AUC",
        "Train_F1Score_PercentileThresholding", "Train_AVERAGE_PRECISION", "Train_PR_AUC", "Train_FIXED_RANGE_PR_AUC"];
    const [dataWithAnomaly, setDataWithAnomaly] = useState<[]>([]);
    const [dataWithoutAnomaly, setDataWithoutAnomaly] = useState<[]>([]);

    useEffect(() => {
        if (encodedValue == "") {
            return;
        }

        Papa.parse(`https://raw.githubusercontent.com/2er0/mTADS/main/results/srb-by-sequence/${encodedValue}.csv`,
            {
                download: true,
                header: true,
                dynamicTyping: true,
                complete: (results) => {
                    console.log(results)
                    setDataWithAnomaly(results.data as []);
                },
                error: (error) => {
                    console.log(error);
                }
            });

        Papa.parse(`https://raw.githubusercontent.com/2er0/mTADS/main/results/srb-by-sequence/${encodedValue}-no-anomaly.csv`,
            {
                download: true,
                header: true,
                dynamicTyping: true,
                complete: (results) => {
                    setDataWithoutAnomaly(results.data as []);
                },
                error: (error) => {
                    console.log(error);
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
                    &nbsp;| Semi-realistic benchmark suite
                </h1>
            </div>
            <div className="flex flex-col min-h-screen">
                <Dropdown options={options} baseUrl={baseUrl}/>
                <div className="flex flex-col w-full" style={{minHeight: 960}}>
                    {dataWithAnomaly.length != 0 &&
                        <SimpleDataTable name={encodedValue} columns={columns} data={dataWithAnomaly}/>
                    }
                    {dataWithoutAnomaly.length != 0 &&
                        <SimpleDataTable name={`${encodedValue}-no-anomaly`} columns={columns}
                                         data={dataWithoutAnomaly}/>
                    }
                </div>
                {" "}
                <footer className="flex items-center justify-center w-full h-24 border-t">
                    <p className="mr-1">Laget av</p>
                    <Link href="https://github.com/villi02">
                        <p className="hover:text-pink-400">Vilhjalmur Arnar Vilhjalmsson</p>
                    </Link>
                </footer>
            </div>
        </div>
    )
        ;
};

export default Page;

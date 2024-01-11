"use client"

import { ColumnDef } from "@tanstack/react-table"

// This type is used to define the shape of our data. e.g we want our id to be string and status none other than these four options
export type DatasetResults = {
  index: number
  dataset: string
  rtype: string
  Test_AVERAGE_PRECISION: number
  Test_F1Score_PercentileThresholding: number
  Test_FIXED_RANGE_PR_AUC: number
  Test_PR_AUC: number
  Test_RANGE_PR_AUC: number
  Test_ROC_AUC: number
  Test_THRESHOLD: number
  Train_AVERAGE_PRECISION: number
  Train_F1Score_PercentileThresholding: number
  Train_FIXED_RANGE_PR_AUC: number
  Train_PR_AUC: number
  Train_RANGE_PR_AUC: number
  Train_ROC_AUC: number
}

export const columns: ColumnDef<DatasetResults>[] = [
  {
    accessorKey: "index",
    header: "Run",
  },
  {
    accessorKey: "dataset",
    header: "Dataset",
  },
  {
    accessorKey: "rtype",
    header: "Method",
  },
]
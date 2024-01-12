import React from "react";

export default function SimpleDataTable({ name, columns, data } : {
    name: string, columns: string[], data: any[] }) {
    return (
        <div className="pb-3">
            <hr/>
            <div className="flex">
                <h2 className="text-3xl font-bold p-4">
                    {name}
                </h2>
            </div>
            <table>
                <thead>
                <tr key="-1">
                    {columns.map((item, index) => (
                        <th key={index}>{item}</th>
                    ))}
                </tr>
                </thead>
                <tbody>
                {data.map((item, row_index) => (
                    <tr key={item["index"]}>
                        {columns.map((column, col_index) => (
                            <td key={item["index"]}>{item[column]}</td>
                        ))}
                    </tr>
                ))}
                </tbody>
            </table>
        </div>
    );
}
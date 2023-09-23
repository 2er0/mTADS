"use client";
import React from "react";
import Link from "next/link";
import Dropdown from "../../components/dropdownMenu";

const Page = () => {
  // options for the dropdown menu
  const options = ["Option 1", "Option 2", "Option 3alskjødhføkajsf"];

  return (
    <div>
      <div className="flex flex-col min-h-screen">
        <Dropdown options={options} />
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

"use client";
import React, {useState, useRef} from "react";
import {useRouter} from "next/navigation";

type DropdownProps = {
    options: string[];
    baseUrl: string;
};

export default function Dropdown({options, baseUrl}: DropdownProps) {
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef(null);
    const router = useRouter();

    const handleClick = (e: any) => {
        if (dropdownRef.current === e.target) {
            console.log("Dropdown click detected.");
            return;
        }
        setIsOpen(false);
        console.log("Dropdown closed.");
    };

    const handleEscape = (e: any) => {
        if (e.key === "Escape") {
            setIsOpen(false);
            console.log("Dropdown closed.");
        }
    };

    const toggleDropdown = () => {
        setIsOpen(!isOpen);
        console.log(isOpen ? "Dropdown opened." : "Dropdown closed.");
    };

    return (
        <div className="relative inline-block" ref={dropdownRef}>
            <button
                onClick={toggleDropdown}
                className="py-2 px-3 bg-gray-800 text-white rounded focus:outline-none"
            >
                Select data to visualize
            </button>
            {isOpen && (
                <div
                    className={`absolute mt-2 rounded-md shadow-lg bg-gray-800 divide-y divide-gray-700 overflow-y-auto max-h-60`}>
                    <div className="py-1">
                        {options.map((option, index) => (
                            <a
                                key={index}
                                onClick={(e) => {
                                    const encodedValue = encodeURIComponent(option);
                                    router.push(`/${baseUrl}?q=${encodedValue}`);
                                }}
                                className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-600 hover:text-white cursor-pointer"
                            >
                                {option}
                            </a>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

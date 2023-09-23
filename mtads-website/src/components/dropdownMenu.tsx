import React, { useState, useRef } from "react";

type DropdownProps = {
  options: string[];
};

export default function Dropdown({ options }: DropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

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
        className="py-2 px-3 bg-blue-500 text-white rounded focus:outline-none"
      >
        Toggle Dropdown
      </button>
      {isOpen && (
        <div
          className={`absolute mt-2 rounded-md shadow-lg bg-white divide-y divide-gray-100 z-10`}
        >
          <div className="py-1">
            {options.map((option, index) => (
              <a
                key={index}
                href="#"
                className="block px-4 py-2 text-sm text-gray-700 hover:bg-blue-500 hover:text-white"
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

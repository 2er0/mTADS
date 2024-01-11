import Head from "next/head";
import Link from "next/link";

export default function Home() {

    return (
        <div className="flex flex-col items-center justify-center min-h-screen py-2">
            <Head>
                <title>Create Next App</title>
                <link rel="icon" href="/favicon.ico"/>
            </Head>

            <main className="flex flex-col items-center justify-center w-full flex-1 px-20 text-center">
                <a href="https://github.com/2er0/mTADS/tree/main">
                    <img src="./logo.png" style={{width: 200}} className="mb-10"/>
                </a>
                <h1 className="text-5xl font-bold">
                    Welcome to {" "}
                    <a className="text-blue-450">Multivariate Time Series Anomaly Detection Benchmark Suites</a>
                </h1>

                <p className="mt-5 text-3xl">Benchmark Suites for Anomaly Detection on Multivariate Time Series</p>

                <div className="flex flex-wrap items-center justify-around max-w-4xl mt-6 sm:w-full">
                    <a
                        href="/mTADS/fsb-visualize"
                        className="p-4 mt-6 text-left border w-96 rounded-xl hover:text-blue-600 focus:text-blue-600"
                    >
                        <h3 className="text-2xl font-bold">Visualize FSB &rarr;</h3>
                        <p className="mt-4 text-xl">Visualize the fully synthetic benchmark suite</p>
                    </a>
                    <a
                        href="/mTADS/srb-visualize"
                        className="p-4 mt-6 text-left border w-96 rounded-xl hover:text-blue-600 focus:text-blue-600"
                    >
                        <h3 className="text-2xl font-bold">Visualize SRB &rarr;</h3>
                        <p className="mt-4 text-xl">Visualize the semi-realistic benchmark suite</p>
                    </a>
                </div>
                <div className="flex flex-wrap items-center justify-around max-w-4xl mt-6 sm:w-full">
                    <a
                        href="/mTADS/fsb-results"
                        className="p-4 mt-6 text-left border w-96 rounded-xl hover:text-blue-600 focus:text-blue-600"
                    >
                        <h3 className="text-2xl font-bold">FSB Result Table &rarr;</h3>
                        <p className="mt-4 text-xl">View the result tables</p>
                    </a>
                    <a
                        href="/mTADS/srb-results"
                        className="p-4 mt-6 text-left border w-96 rounded-xl hover:text-blue-600 focus:text-blue-600"
                    >
                        <h3 className="text-2xl font-bold">SRB Result Table &rarr;</h3>
                        <p className="mt-4 text-xl">View the result tables</p>
                    </a>
                </div>
                <div className="flex flex-wrap items-center justify-around max-w-4xl mt-6 sm:w-full">
                    <Link
                        href="https://github.com/2er0/mTADS/tree/main"
                        className="p-4 mt-6 text-left border w-96 rounded-xl hover:text-blue-600 focus:text-blue-600"
                    >
                        <h3 className="text-2xl font-bold">mTADS repository &rarr;</h3>
                        <p className="mt-4 text-xl">Get mTADS from GitHub</p>
                    </Link>
                    <Link
                        href="https://www.ntnu.edu/norwai"
                        className="p-4 mt-6 text-left border w-96 rounded-xl hover:text-blue-600 focus:text-blue-600"
                    >
                        <h3 className="text-2xl font-bold">About NorwAI &rarr;</h3>
                        <p className="mt-4 text-xl">Learn More About NorwAI</p>
                    </Link>
                </div>
            </main>
            <footer className="flex items-center justify-center w-full h-24 border-t">
                <p className="mr-1">Made By</p>
                <Link href="https://github.com/villi02">
                    <p className="hover:text-pink-400">Vilhjalmur Arnar Vilhjalmsson</p>
                </Link>
            </footer>
        </div>
    );
}

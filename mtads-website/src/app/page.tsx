import Head from "next/head";
import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen py-2">
      <Head>
        <title>Create Next App</title>
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="flex flex-col items-center justify-center w-full flex-1 px-20 text-center">
        <h1 className="text-5xl font-bold">
          Welcome to {" "}
          <a className="text-blue-450">Multivariate Time Series Anomaly Detection Benchmark Suits</a>
        </h1>

        <p className="mt-5 text-3xl">Benchmark Suits for Anomaly Detection on Multivariate Time Series</p>

        <div className="flex flex-wrap items-center justify-around max-w-4xl mt-6 sm:w-full">
          <Link
            href="https://www.ntnu.edu/norwai"
            className="p-4 mt-6 text-left border w-96 rounded-xl hover:text-blue-600 focus:text-blue-600"
          >
            <h3 className="text-2xl font-bold">About NorwAI &rarr;</h3>
            <p className="mt-4 text-xl">Learn More About NorwAI</p>
          </Link>
          <a
            href="/visualize"
            className="p-4 mt-6 text-left border w-96 rounded-xl hover:text-blue-600 focus:text-blue-600"
          >
            <h3 className="text-2xl font-bold">Visualize &rarr;</h3>
            <p className="mt-4 text-xl">Visualize the data</p>
          </a>
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

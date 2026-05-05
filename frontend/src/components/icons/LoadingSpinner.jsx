export default function LoadingSpinner(){
    return (

        <div 
            className="w-100 d-flex justify-content-center align-content-center"
        >
            <svg
                className="loading-spinner"
                xmlns="http://www.w3.org/2000/svg"
                shapeRendering="geometricPrecision"
                textRendering="geometricPrecision"
                viewBox="0 0 300 300"
            >
                <defs>
                    <linearGradient
                        id="a"
                        x1={0}
                        x2={1}
                        y1={0.5}
                        y2={0.5}
                        gradientUnits="objectBoundingBox"
                        spreadMethod="pad"
                    >
                        <stop offset="0%" stopColor="rgba(210,219,237,0)" />
                        <stop offset="100%" stopColor="#686868" />
                    </linearGradient>
                </defs>
                <path
                    fill="url(#a)"
                    d="M150 10c77.32 0 140 62.68 140 140h-20c0-66.274-53.726-120-120-120S30 83.726 30 150H10C10 72.68 72.68 10 150 10Z"
                />
            </svg>
        </div>
    )
}

import React from 'react'


class GraphIcon extends React.Component {
  render() {
    return (
      <svg viewBox="0 0 1000 1000" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlnsXlink="http://www.w3.org/1999/xlink">
        <defs>
          <circle id="path-1" cx="215" cy="745" r="71"></circle>
          <filter x="-4.9%" y="-3.5%" width="109.9%" height="109.9%" filterUnits="objectBoundingBox" id="filter-2">
            <feOffset dx="0" dy="2" in="SourceAlpha" result="shadowOffsetOuter1"></feOffset>
            <feGaussianBlur stdDeviation="2" in="shadowOffsetOuter1" result="shadowBlurOuter1"></feGaussianBlur>
            <feColorMatrix values="0 0 0 0 0   0 0 0 0 0   0 0 0 0 0  0 0 0 0.5 0" type="matrix" in="shadowBlurOuter1"></feColorMatrix>
          </filter>
          <circle id="path-3" cx="665" cy="205" r="55"></circle>
          <filter x="-6.4%" y="-4.5%" width="112.7%" height="112.7%" filterUnits="objectBoundingBox" id="filter-4">
            <feOffset dx="0" dy="2" in="SourceAlpha" result="shadowOffsetOuter1"></feOffset>
            <feGaussianBlur stdDeviation="2" in="shadowOffsetOuter1" result="shadowBlurOuter1"></feGaussianBlur>
            <feColorMatrix values="0 0 0 0 0   0 0 0 0 0   0 0 0 0 0  0 0 0 0.5 0" type="matrix" in="shadowBlurOuter1"></feColorMatrix>
          </filter>
          <ellipse id="path-5" cx="363" cy="432.5" rx="110" ry="109.5"></ellipse>
          <filter x="-3.2%" y="-2.3%" width="106.4%" height="106.4%" filterUnits="objectBoundingBox" id="filter-6">
            <feOffset dx="0" dy="2" in="SourceAlpha" result="shadowOffsetOuter1"></feOffset>
            <feGaussianBlur stdDeviation="2" in="shadowOffsetOuter1" result="shadowBlurOuter1"></feGaussianBlur>
            <feColorMatrix values="0 0 0 0 0   0 0 0 0 0   0 0 0 0 0  0 0 0 0.5 0" type="matrix" in="shadowBlurOuter1"></feColorMatrix>
          </filter>
          <circle id="path-7" cx="132.5" cy="132" r="95"></circle>
          <filter x="-3.7%" y="-2.6%" width="107.4%" height="107.4%" filterUnits="objectBoundingBox" id="filter-8">
            <feOffset dx="0" dy="2" in="SourceAlpha" result="shadowOffsetOuter1"></feOffset>
            <feGaussianBlur stdDeviation="2" in="shadowOffsetOuter1" result="shadowBlurOuter1"></feGaussianBlur>
            <feColorMatrix values="0 0 0 0 0   0 0 0 0 0   0 0 0 0 0  0 0 0 0.5 0" type="matrix" in="shadowBlurOuter1"></feColorMatrix>
          </filter>
        </defs>
        <g stroke="none" strokeWidth="1" fill="none" fillRule="evenodd">
          <g id="circles" transform="translate(80.000000, 51.000000)">
            <g id="lines" transform="translate(129.000000, 125.000000)" stroke="#39505D" strokeLinecap="square" strokeWidth="40">
              <path d="M0,0 L230,312" id="Line"></path>
              <path d="M535,79 L230,312" id="Line-2"></path>
              <path d="M230,301 L80,628" id="Line-4"></path>
            </g>
            <circle id="Oval" fill="#39505D" cx="132.5" cy="132.5" r="132.5"></circle>
            <circle id="Oval-Copy" fill="#39505D" cx="362.5" cy="432.5" r="162.5"></circle>
            <circle id="Oval-Copy-5" fill="#39505D" cx="215" cy="745" r="110"></circle>
            <g id="Oval">
              <use fill="black" fillOpacity="1" filter="url(#filter-2)" xlinkHref="#path-1"></use>
              <use fill="#42D5C2" fillRule="evenodd" xlinkHref="#path-1"></use>
            </g>
            <circle id="Oval-Copy-2" fill="#39505D" cx="664.5" cy="205.5" r="92.5"></circle>
            <g id="Oval-Copy-2">
              <use fill="black" fillOpacity="1" filter="url(#filter-4)" xlinkHref="#path-3"></use>
              <use fill="#FDD600" fillRule="evenodd" xlinkHref="#path-3"></use>
            </g>
            <g id="Oval">
              <use fill="black" fillOpacity="1" filter="url(#filter-6)" xlinkHref="#path-5"></use>
              <use fill="#FFFFFF" fillRule="evenodd" xlinkHref="#path-5"></use>
            </g>
            <g id="Oval">
              <use fill="black" fillOpacity="1" filter="url(#filter-8)" xlinkHref="#path-7"></use>
              <use fill="#59A9FA" fillRule="evenodd" xlinkHref="#path-7"></use>
            </g>
          </g>
        </g>
      </svg>
    )
  }
}


export default GraphIcon

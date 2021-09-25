const classNames = (classNames='', conditionalClassNames={}) => (
  `${classNames} `.concat(Object.keys(conditionalClassNames).filter(key => (
    conditionalClassNames[key]
  )).join(' '))
)

export default classNames

export type DocumentPage = {
  page_number: number
  text: string
}

export type DocumentExtraction = {
  filename: string
  page_count: number
  pages: DocumentPage[]
  warnings: string[]
}

export function isDocumentExtraction(value: unknown): value is DocumentExtraction {
  if (typeof value !== 'object' || value === null) return false
  return (
    'filename' in value && typeof value.filename === 'string' &&
    'page_count' in value && Number.isInteger(value.page_count) &&
    'pages' in value && Array.isArray(value.pages) &&
    value.page_count === value.pages.length &&
    value.pages.every((page: unknown) => (
      typeof page === 'object' && page !== null &&
      'page_number' in page && Number.isInteger(page.page_number) &&
      'text' in page && typeof page.text === 'string'
    )) &&
    'warnings' in value && Array.isArray(value.warnings) &&
    value.warnings.every((warning: unknown) => typeof warning === 'string')
  )
}

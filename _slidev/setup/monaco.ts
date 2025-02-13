// ./setup/monaco.ts
import { defineMonacoSetup } from '@slidev/types'

export default defineMonacoSetup(() => {
  return {
    editorOptions: {
      fontSize: '16px',
      fontWeight: '500',
      lineHeight: '18px',
      lineNumbers: 'on',
      wordWrap: 'off',
      fontLigatures: true,
      renderLineHighlightOnlyWhenFocus: true,
      fontVariations: 'normal',
      showFoldingControls: 'never',
      guides: {
        indentation: false,
      },
      lineDecorationsWidth: false,
      matchBrackets: 'near',
      columnSelection: false,
      
    },
  }
})

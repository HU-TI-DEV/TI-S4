import { defineCodeRunnersSetup } from '@slidev/types'

export default defineCodeRunnersSetup(() => {
  return {
    cpp: async (code: string, ctx) => {
      // Use a compiler id from runner options, or default to 'clang_trunk'
      const compilerId = (ctx.options.compilerId as string) || 'clang_trunk'

      // Build the payload for the Godbolt API
      const payload = {
        source: code,
        compiler: compilerId,
        options: {
          // Allow passing custom compiler flags if desired
          userArguments: (ctx.options.userArguments as string) || "",
          // Request execution of the compiled code
          compilerOptions: { executorRequest: true },
          // Enable execution filter so the code runs
          filters: { execute: true }
        },
        lang: 'c++',
        allowStoreCodeDebug: false
      }

      try {
        const response = await fetch(`https://godbolt.org/api/compiler/${compilerId}/compile`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify(payload)
        })

        if (!response.ok) {
          return { text: `Error: ${response.status} ${response.statusText}` }
        }

        const result = await response.json()

        // Combine stdout and stderr outputs (if any)
        const stdout = Array.isArray(result.stdout)
          ? result.stdout.map((line: { text: string }) => line.text).join("\n")
          : ""
        const stderr = Array.isArray(result.stderr)
          ? result.stderr.map((line: { text: string }) => line.text).join("\n")
          : ""
        const output = stdout + (stderr ? "\n" + stderr : "")
        return { text: output }
      } catch (error: any) {
        return { text: `Error: ${error.message || error}` }
      }
    }
  }
})

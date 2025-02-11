import { defineCodeRunnersSetup } from '@slidev/types'
import Convert from 'ansi-to-html'

const convert = new Convert()

export default defineCodeRunnersSetup(() => {
  return {
    cpp: async (code: string, ctx) => {
      // Allow users to override the default compiler and arguments via runnerOptions.
      const compilerId = (ctx.options.compilerId as string) || 'clang_trunk';
      const userArguments = (ctx.options.userArguments as string) || "";

      // Construct the payload for the Godbolt API.
      const payload = {
        source: code,
        compiler: compilerId,
        options: {
          userArguments,
          compilerOptions: { executorRequest: true },
          filters: { execute: true }
        },
        lang: 'c++',
        allowStoreCodeDebug: false
      };

      try {
        const response = await fetch(`https://godbolt.org/api/compiler/${compilerId}/compile`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify(payload)
        });

        if (!response.ok) {
          return { text: `Error: ${response.status} ${response.statusText}` };
        }

        const result = await response.json();

        // Prefer buildResult if present; otherwise, work directly with the result.
        const buildResult = result.buildResult.code ? result.buildResult : result;

        // Collect stdout and stderr from the build result.
        const stdout = Array.isArray(buildResult.stdout)
          ? buildResult.stdout.map((line: { text: string }) => line.text).join("\n")
          : "";
        const stderr = Array.isArray(buildResult.stderr)
          ? buildResult.stderr.map((line: { text: string }) => line.text).join("\n")
          : "";

        // If the build failed (nonzero code), prepend the failure message.
        let output: string;
        if (buildResult.code !== 0) {
          output = `Build failed, return code: ${buildResult.code}\n` + stdout + (stderr ? "\n" + stderr : "");
        } else {
          output = stdout + (stderr ? "\n" + stderr : "");
        }

        console.log(output)

        // Process ANSI escape codes into HTML formatting and wrap it in a pre tag.
        // Process ANSI escape codes with ansi2html-extended.
        // We pass config to not wrap the content in an extra span and to produce an HTML chunk.
        const htmlOutput = `<pre>${convert.toHtml(output)}</pre>`
        return { html: htmlOutput };
      } catch (error: any) {
        return { text: `Error: ${error.message || error}` };
      }
    }
  }
});

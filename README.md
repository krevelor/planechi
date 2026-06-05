# The Hadwiger-Nelson problem

The Hadwiger-Nelson problem (https://en.wikipedia.org/wiki/Hadwiger%E2%80%93Nelson_problem) is an open problem which asks what the chromatic number of the unit graph of the plane is. When introduced, it was shown that the answer is trivially bounded to be between 4 and 7, inclusive. In the decades since, researchers have managed to find a graph which proves the answer is at least 5, but the exact answer is still unknown.
When first learning about this problem, and seeing how much "wiggle room" the n=7 solution has, it seemed natural to me to question how it was that no one had found a solution for n=6. Various ideas would spring to mind, but after some geometric working out would always prove too simplistic. The more I thought about it, the more I desired to have a way to visualize the "exculsion shadow" of a region - the area which is one unit away from some part of it. From this followed a fairly natural idea - once I had the ability to measure these collisions at scale, couldn't I attempt to stochastically generate a solution for n=6?

## My approach

Most of the work I've done on this problem has been on the latter objective. I was working off of two general assumptions:
 - If a solution for n=6 exists, it seems plausible that one exists which is not infinitely fine - one where at least large portions of the plane are divided into macroscopic contiguous regions, similar to the n=7 solution
 - If a solution for n=6 exists, there most likely exists a repeating solution as well, similar to the infinite tiling of the n=7 solution. Given the local nature of the unit length edges, it seems conceptually unlikely that the only solution is globally asymmetric

I want to stress that these are fully *assumptions*. I have no way to back them up, but they seemed reasonable enough, and are required for the approach I wanted to investigate here to be able to find a solution. I was of course aware it was perfectly likely one or both were false, but I figured messing around with the code would at the very least shed some insight into why they were untrue. In fact, as I had already begun to suspect from running a few dozen generations and examining the outputs, the first assumption has been proven false (see below).

With the baseline assumptions out of the way, my idea was to take a grid of pixels, and work out which pixels are connected on a condensed version of the unit graph. From there, it could randomly recolor pixels which had a particularly high number of collisions, with the goal of probabilistically approaching a solution. Delightfully, the program almost immediately started doing what you'd expect - producing images with clumps of color just smaller than one unit across. Of course, with only six colors, the edges of these clumps were always too close together and the like, but it was still fascinating seeing it head in the right direction with no further prompting.

After refinement and experimenting with parameters, I've been able to produce many interesting paterns, several matching ideas I'd wondered about before starting this project, but none of them were particularly close to being true solutions. All exhibit the issue of regions being a bit too large, or a bit too close together. Some even exhibit explicit dead zones, where the program appears to have no idea how to color a section of the plane. While I continued to work on new approaches, such as taking in input images to attempt refinements on past runs and the like, it was becoming increasingly obvious that this approach was not going to produce the solution I was hoping. Nevertheless it's been very enjoyable producing these images, and working on other approaches to viewing the problem.

## Assumptions are, well, assumptions

Unfortunately for me, while I had done some research on work on the problem, I had neglected to look into variations on the problem. As it turns out, the work of Voronov (https://arxiv.org/pdf/2304.10163) showed last year that solutions of the kind I've been searching for (in particular, those following my first assumption above) necessarily have n=7. Indeed, from the sounds of it earlier work by Thomassen also ruled out these sort of solutions, but as of this writing I have not yet read that paper.

In light of this, I believe I will be primarily cleaning up the project and then considering it finished. While I hope to continue working on this problem in the future, it is unfortunately the case that any solution for n=6 would not be one what could be properly represented by a computer, at least in such a simplistic way. Despite this, I've really enjoyed working on this project, and the deeper understanding of the larger problem it has provided.

Anyone is free to use and adapt the code herein as they see fit, as long as I am creditted for it. I hope someone finds a way to apply this work productively, even if it isn't me. :)

# The actual README part

exclusion ring.py is the main class for all things generation. Parameters are set internally (found near the top of the file) and the numeric ones (not the file names) are output at run time to assist with labeling. 
The main parameters to note are:
 - cn: the number of colors to use. for all my searching this was 6
 - n: the number of iterations to run. I found very little return after the first few thousand, so I would not suggest putting about 5000 at the absolute max, and even on a powerful pc that will take several hours for a modest grid size
 - gsz: the grid size. from the assumption of a repeating tiling above, this is the size of the repeating tiling, so exclusion rings wrap around the edges of the grid. while the area doesn't have to be square, I never saw much of a reason to implement a non square region, but inputting an image *should* handle non square images
 - rsq: how many squares equals 1 unit. In other words, the grid scale is one square equals 1/rsq unit.

The interplay between rsq and gsz largely determines the behavior of the generation. In particular, since there's no benefit to rsq > gsz, the current implementation will not handle that properly. In addition, I found that when rsq/gsz is greater than around 1/root(2), the generation becomes incredible unstable, and generally does not produce anything of value. The reason why can be seen from the exclusion ring - at those scales, the exclusion ring wraps back and forth over the grid so much as to occupy most of it, preventing large regions from forming.

In additon to the input and output grids, the program produces a before and after density grid. You can see the details in the code, but the general idea is that a pure green pixel indicates that cell has zero collisions, and more collisions means redder cells, up to a theoretical maximum at 64% of possible collisions. From these images, you can see that even in cases where it looks to be getting close, strips of problem pixels run between the regions with no real way to resolve them.


There are various other auxillary programs I've created in the process of working on this, and those will be uploaded once they are cleaned up.

using CLEARSWI

if isassigned(ARGS, 1)
    nobrackets = replace(ARGS[1], r"\[|\]" => "")
    nobrackets = replace(nobrackets, r"]" => "")
    TEstrings = split(nobrackets, ",")
    TEs = Array{Int}(undef, length(TEstrings))

    for i = 1:length(TEstrings)
        input = TEstrings[i]
        TEs[i] = parse(Int64, input)
    end
else
    TEs = [20]
end

println("TEs based on input:")
println(TEs)

nifti_folder = "/01_bids/sub-xxxx/ses-1/anat"

magfile = joinpath(nifti_folder, "sub-xxxx_ses-1_acq-qsm_run-1_magnitude.nii.gz")
phasefile = joinpath(nifti_folder, "sub-xxxx_ses-1_acq-qsmPH00_run-1_phase.nii.gz")

mag = readmag(magfile);
phase = readphase(phasefile);
data = Data(mag, phase, mag.header, TEs);

swi = calculateSWI(data);
# mip = createIntensityProjection(swi, minimum); # minimum intensity projection, other Julia functions can be used instead of minimum
mip = createMIP(swi); # shorthand for createIntensityProjection(swi, minimum)

savenii(swi, "/root/clearswi_output/swi.nii"; header=mag.header)
savenii(mip, "/root/clearswi_output/mip.nii"; header=mag.header)
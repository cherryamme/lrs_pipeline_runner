#!/bin/bash

HELP="🅾 Usage: $(basename $0) config_file
🅾 ---------------------------------------
🅾 <config_file> : /home/long_read/LRS/script/Lrs_thal_pipeline2/source/lrs_thal.config
🅾 <note> : use to run long read THAL pipeline
🅾 ---------------------------------------
🅾 author :Jc"

usage() {
	cat <<-EOF >&2
		🟥🟧🟨🟨🟩🟦🟪🟫 🤡 HELP 🤡 🟫🟪🟦🟩🟨🟧🟥
		$HELP
		🟥🟧🟨🟨🟩🟦🟪🟫⬛⬛⬛⬛⬛⬛🟫🟪🟦🟩🟨🟧🟥
	EOF
	exit 1
}

check_args() {
	(($# != 1)) || [[ ! -e $1 ]] && usage
}

load_config() {
	raw_config=$1
	echo "loading config"
	. $raw_config
	}

check_config() {
	[[ -z $VERSION ]] || [[ -z $function_sh ]] && echo "ERROR: config file illegal; there is no VERSION or function_sh" && usage
}

check_singularity() {
	if command -v "$singularity" > /dev/null; then
		echo "Run singularity mode"
		[[ ! -e $singularity_img ]] && echo "ERROR: singularity_img not exist: $singularity_img"
	else
		. $function_sh
		[[ ! -e $pipeline_dir ]] && echo "ERROR: pipeline_dir not exist: $pipeline_dir"
	fi
}

prepare_output() {
	mkdir -p $outdir/{logs,index,config,shell}
	back_config=$outdir/$(basename $raw_config).back
	cp -f $raw_config $back_config
}

update_config() {
	local barcode_id=$1
	local docker=$2
	sed -e "s@^inputdata=.*@inputdata=$inputdata/$barcode_id@" \
		-e "s@^outdir=.*@outdir=$outdir/$barcode_id@" \
		-e "s@^index_file=.*@index_file=$outdir/index/$barcode_id.index@" \
		$raw_config >"$outdir/config/${barcode_id}.config"
	if [[ $docker == "TRUE" ]]; then
		sed -i -e 's/\.sh//g' -e 's|\(pipeline_dir=\).*|\1/pipeline|g' $outdir/config/${barcode_id}.config
	fi
}

run_pipeline() {
	for barcode_id in $(awk -v outdir="$outdir" -F'\t' '(!/^#/){print $1"\t"$2"\t"$3 > outdir"/index/"$1".index";print $1}' $index_file | sort | uniq); do
		barcode_dir=$inputdata/$barcode_id
		if ! command -v "$singularity" > /dev/null || [[ ! -e "$singularity_img" ]]; then
			update_config $barcode_id
			echo "$s_run $outdir/config/${barcode_id}.config || exit 100" >${outdir}/shell/${barcode_id}_script.sh
			command="$s_run $outdir/config/${barcode_id}.config"
		else
			update_config $barcode_id TRUE
			configdir=$(dirname $index_file)
			echo "s_run $outdir/config/${barcode_id}.config || exit 100" >${outdir}/shell/${barcode_id}_script.sh
			command="$singularity exec -e --bind ${inputdata},${outdir},${configdir} $singularity_img /bin/bash ${outdir}/shell/${barcode_id}_script.sh"
		fi
		execute_command "$command" "$barcode_id"
	done
}

execute_command() {
	local command=$1
	local barcode_id=$2
	if [[ -z "$qsub" ]]; then
		echo "<command>: $command"
		$command > >(tee $outdir/logs/run_${barcode_id}.o) 2> >(tee $outdir/logs/run_${barcode_id}.e >&2)
	else
		echo "<comand>: $qsub -N ${batch}_${barcode_id} $command" 2>&1 > >(tee -a ${outdir}/shell/batch.submit) 
		pid=$($qsub -N ${batch}_${barcode_id} -o $outdir/logs/run_${barcode_id}.o -e $outdir/logs/run_${barcode_id}.e $command)
		barcode_array+=($pid)
	fi
}


generate_summary() {
	if ! command -v "$singularity" > /dev/null || [[ ! -e "$singularity_img" ]]; then
		command="$batch_summary $back_config"
	else
		configdir=$(dirname $index_file)
		echo "batch_summary <(sed -e 's/\.sh//g' -e 's|\(pipeline_dir=\).*|\1/pipeline|g' $back_config)" >${outdir}/shell/batch_summary.sh
		command="$singularity exec -e --bind ${inputdata},${outdir},${configdir} $singularity_img /bin/bash ${outdir}/shell/batch_summary.sh"
	fi
	execute_summary_command "$command"
}

execute_summary_command() {
	local command=$1
	if [[ -z "$qsub" ]]; then
		$command > >(tee $outdir/logs/batch_summary.o) 2> >(tee $outdir/logs/batch_summary.e >&2)
	else
		echo "<comand>: $qsub -N ${batch}_summary -hold_jid "$(IFS=,; echo "${barcode_array[*]}")" $command" 2>&1 > >(tee -a ${outdir}/shell/batch.submit) 
		pid=$($qsub -N ${batch}_summary -hold_jid "$(IFS=,; echo "${barcode_array[*]}")" -o $outdir/logs/batch_summary.o -e $outdir/logs/batch_summary.e $command)
		echo "$(date) 已投递 batch_summary: ${pid}"
	fi
}


main() {
	check_args "$@"
	load_config "$1"
	check_config
	check_singularity
	prepare_output
	run_pipeline
	generate_summary
}

main "$@"
